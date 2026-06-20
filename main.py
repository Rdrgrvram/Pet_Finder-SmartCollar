# ════════════════════════════════════════════════════════════════════
#  PetFinder Smart Collar — Script principal MicroPython
#  Hardware : ESP32 DevKit V1 (38 pines)
#             NTC 10K   → GPIO 36 / VP  (divisor de voltaje con R 10K a GND)
#             SW-520D   → GPIO 18       (sensor de vibración)
#             Buzzer    → GPIO 19       (vía transistor NPN 2N2222A + R 2K)
#             GPS NEO-M8L → UART2 TX=GPIO17 RX=GPIO16 @ 115200
#  Protocolo: WiFi → Supabase REST API (HTTPS)
#  Autor    : PetFinder Team
# ════════════════════════════════════════════════════════════════════

import network, urequests, ujson, time, machine, math, gc
from machine import Pin, UART, ADC
from secrets import WIFI_SSID, WIFI_PASSWORD, SUPABASE_URL, SUPABASE_ANON_KEY

print("Iniciando componentes...")
time.sleep(2)

# ── Tablas Supabase ──────────────────────────────────────────────────
TABLA_LECTURAS    = "lecturas_collar"
TABLA_COMANDOS    = "comandos"
INTERVALO_CICLO   = 10

# ── Constantes NTC 10K (Beta) ────────────────────────────────────────
NTC_BETA          = 3950
NTC_R_NOMINAL     = 10000
NTC_T_NOMINAL     = 25
NTC_R_SERIE       = 10000
ADC_RESOLUCION    = 4095
ADC_VREF          = 3.3

# ── Pines ────────────────────────────────────────────────────────────
led    = Pin(2, Pin.OUT)          # LED integrado del DevKit V1
buzzer = Pin(19, Pin.OUT)         # GPIO 19 → resistencia 2K → base transistor
vibra  = Pin(18, Pin.IN, Pin.PULL_UP)  # SW-520D en GPIO 18

# NTC 10K en GPIO 36 (VP) — pin ADC de solo entrada, sin PULL
adc_ntc = ADC(Pin(36))
adc_ntc.atten(ADC.ATTN_11DB)     # Rango 0–3.6V
adc_ntc.width(ADC.WIDTH_12BIT)   # Resolución 12 bits (0–4095)

# GPS NEO-M8L en UART2 — TX=GPIO17, RX=GPIO16
# Confirmado a 115200 baudios en pruebas de hardware estables.
gps = UART(2, baudrate=115200, tx=17, rx=16)

wlan = network.WLAN(network.STA_IF)


# ════════════════════════════════════════════════════════════════════
#  UTILIDADES
# ════════════════════════════════════════════════════════════════════

def blink(n=1, ms=100):
    for _ in range(n):
        led.value(1); time.sleep_ms(ms)
        led.value(0); time.sleep_ms(ms)


def activar_buzzer(segundos=1):
    print(f"[BUZZER] Activando por {segundos}s")
    buzzer.value(1)
    time.sleep(segundos)
    buzzer.value(0)
    print("[BUZZER] Apagado")


# ════════════════════════════════════════════════════════════════════
#  CONECTIVIDAD WiFi
# ════════════════════════════════════════════════════════════════════

def conectar_wifi():
    if wlan.isconnected():
        return True

    print(f"[WiFi] Conectando a '{WIFI_SSID}'...")

    for intento in range(5):
        wlan.active(False)
        time.sleep(2)
        wlan.active(True)
        time.sleep(2)

        wlan.config(reconnects=0)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        for i in range(15):
            if wlan.isconnected():
                print("[WiFi] Conectado →", wlan.ifconfig()[0])
                blink(3)
                return True
            time.sleep(1)

        print(f"[WiFi] Intento {intento+1}/5 fallido, reintentando...")
        wlan.active(False)
        time.sleep(1)

    print("[WiFi] Sin conexión tras 5 intentos.")
    return False


# ════════════════════════════════════════════════════════════════════
#  LECTURA DE SENSORES
# ════════════════════════════════════════════════════════════════════

def leer_temperatura():
    """
    Lee el NTC 10K mediante el divisor de voltaje.
    Convierte el valor ADC a temperatura usando la ecuación Beta del NTC.
    """
    try:
        muestras = [adc_ntc.read() for _ in range(10)]
        raw = sum(muestras) // len(muestras)

        if raw <= 0 or raw >= ADC_RESOLUCION:
            print("[TEMP] Lectura ADC fuera de rango — verifica cableado")
            return None

        r_ntc = NTC_R_SERIE * (ADC_RESOLUCION / raw - 1)

        t0_kelvin   = NTC_T_NOMINAL + 273.15
        temp_kelvin = 1.0 / (1.0 / t0_kelvin + math.log(r_ntc / NTC_R_NOMINAL) / NTC_BETA)
        temp_celsius = round(temp_kelvin - 273.15, 1)

        print(f"[TEMP] ADC={raw}  R_NTC={int(r_ntc)}Ω  Temp={temp_celsius}°C")
        return temp_celsius

    except Exception as e:
        print(f"[TEMP] Error: {e}")
        return None


def detectar_movimiento(duracion_ms=2000):
    inicio = time.ticks_ms()
    cambios = 0
    ultimo = vibra.value()

    while time.ticks_diff(time.ticks_ms(), inicio) < duracion_ms:
        actual = vibra.value()

        if actual != ultimo:
            cambios += 1
            ultimo = actual

        time.sleep_ms(10)

    print("Cambios vibración:", cambios)
    return 1 if cambios >= 2 else 0


def _convertir_coordenada(raw, direccion):
    """Convierte coordenada NMEA (DDMM.MMMM / DDDMM.MMMM) a decimal."""
    if not raw or not direccion:
        return None
    try:
        if direccion in ("N", "S"):      # Latitud NMEA: DDMM.MMMM
            g = int(raw[:2])
            m = float(raw[2:])
        else:                            # Longitud NMEA: DDDMM.MMMM
            g = int(raw[:3])
            m = float(raw[3:])
        decimal = g + m / 60.0
        if direccion in ("S", "W"):
            decimal = -decimal
        return round(decimal, 6)
    except:
        return None


def leer_gps(timeout_ms=8000):
    """
    Busca de manera tolerante un Fix válido interrumpiendo tramas GGA y RMC.
    Limpia el búfer UART inicial para asegurar datos del tiempo presente.
    """
    if gps.any():
        gps.read() 
        
    inicio = time.ticks_ms()
    buf = b""
    
    while time.ticks_diff(time.ticks_ms(), inicio) < timeout_ms:
        if gps.any():
            buf += gps.read()
            while b"\n" in buf:
                linea, buf = buf.split(b"\n", 1)
                try:
                    txt = linea.decode('ascii', 'ignore').strip() 
                    
                    # --- Procesar tramas GGA ---
                    if txt.startswith("$GPGGA") or txt.startswith("$GNGGA"):
                        partes = txt.split(",")
                        if len(partes) > 7:
                            calidad = int(partes[6]) if partes[6] else 0
                            if calidad > 0 and partes[2] and partes[4]:
                                lat = _convertir_coordenada(partes[2], partes[3])
                                lon = _convertir_coordenada(partes[4], partes[5])
                                print(f"[GPS] Fix OK (GGA) → lat={lat}  lon={lon} | Sats={partes[7]}")
                                return lat, lon
                            else:
                                print(f"[GPS] Datos GGA detectados... buscando satélites (Sats={partes[7] if partes[7] else 0})")
                                
                    # --- Procesar tramas RMC ---
                    elif txt.startswith("$GPRMC") or txt.startswith("$GNRMC"):
                        partes = txt.split(",")
                        if len(partes) > 6 and partes[2] == "A":
                            lat = _convertir_coordenada(partes[3], partes[4])
                            lon = _convertir_coordenada(partes[5], partes[6])
                            print(f"[GPS] Fix OK (RMC) → lat={lat}  lon={lon}")
                            return lat, lon
                            
                except Exception:
                    pass
        time.sleep_ms(20)
        
    print("[GPS] Sin fix en este ciclo (Buscando señal...)")
    return None, None


# ════════════════════════════════════════════════════════════════════
#  COMUNICACIÓN CON SUPABASE
# ════════════════════════════════════════════════════════════════════

def _headers_supabase():
    return {
        "apikey":        SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type":  "application/json"
    }


def enviar_lectura(temp, mov, lat, lon):
    url  = f"{SUPABASE_URL}/rest/v1/{TABLA_LECTURAS}"
    data = {"movimiento": bool(mov)}
    if temp is not None: data["temperatura"] = temp
    if lat  is not None: data["latitud"]     = lat
    if lon  is not None: data["longitud"]    = lon
    try:
        r = urequests.post(url, headers=_headers_supabase(), data=ujson.dumps(data))
        print(f"[HTTP] Lectura enviada → {r.status_code}")
        if r.status_code not in (200, 201):
            try: print(f"[HTTP] Detalle: {r.text}")
            except: pass
        r.close()
        gc.collect()
        if r.status_code in (200, 201):
            blink(1)
    except Exception as e:
        print(f"[HTTP] Error al enviar: {e}")


def consultar_comando_buzzer():
    url = (f"{SUPABASE_URL}/rest/v1/{TABLA_COMANDOS}"
           f"?ejecutado=eq.false&order=created_at.desc&limit=1")
    try:
        r     = urequests.get(url, headers=_headers_supabase())
        datos = ujson.loads(r.text)
        r.close()
        gc.collect()
        if datos:
            comando = datos[0]
            id_cmd  = comando.get("id")
            accion  = comando.get("accion", "")
            print(f"[CMD] Recibido: {accion} (id={id_cmd})")
            if accion == "buzzer_on":
                activar_buzzer(3)
            elif accion == "buzzer_off":
                buzzer.value(0)
                print("[CMD] Buzzer apagado por comando remoto")
            _marcar_ejecutado(id_cmd)
    except Exception as e:
        print(f"[CMD] Error: {e}")


def _marcar_ejecutado(id_cmd):
    url  = f"{SUPABASE_URL}/rest/v1/{TABLA_COMANDOS}?id=eq.{id_cmd}"
    hdrs = _headers_supabase()
    hdrs["Prefer"] = "return=minimal"
    try:
        r = urequests.patch(url, headers=hdrs, data=ujson.dumps({"ejecutado": True}))
        r.close()
        gc.collect()
        print(f"[CMD] Comando {id_cmd} marcado como ejecutado")
    except Exception as e:
        print(f"[CMD] Error al actualizar comando: {e}")


# ════════════════════════════════════════════════════════════════════
#  BUCLE PRINCIPAL
# ════════════════════════════════════════════════════════════════════

def main():
    print("=" * 50)
    print("  PetFinder Smart Collar — Iniciando...")
    print("=" * 50)
    blink(3)

    conectar_wifi()

    while True:
        print("\n─── NUEVO CICLO ───────────────────────────")

        mov      = detectar_movimiento(2000)
        temp     = leer_temperatura()
        lat, lon = leer_gps(8000)

        print(f"[DATA] temp={temp}°C  mov={mov}  lat={lat}  lon={lon}")

        if not wlan.isconnected():
            print("[WiFi] Reconectando...")
            conectar_wifi()

        if wlan.isconnected():
            enviar_lectura(temp, mov, lat, lon)
            consultar_comando_buzzer()

        time.sleep(INTERVALO_CICLO)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("[ERROR CRÍTICO]", e)
        time.sleep(5)
        machine.reset()