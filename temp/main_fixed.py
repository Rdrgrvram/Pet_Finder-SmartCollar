from machine import UART, Pin
import network, urequests, ujson, time, machine
import dht

# ── Config ──────────────────────────────────────────────────────
WIFI_SSID     = "Redmi Rodri S"
WIFI_PASSWORD = "123456789"
SUPABASE_URL  = "https://kjuoamogxpplpyaseeat.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqdW9hbW9neHBwbHB5YXNlZWF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3OTU1NDUsImV4cCI6MjA5MjM3MTU0NX0.ty8SNcnELPCKk43qoRJft4-8IVQz6GrSouoX4T188CQ"
TABLA         = "lecturas_collar"
INTERVALO     = 10

# ── Hardware ─────────────────────────────────────────────────────
led        = Pin(2,  Pin.OUT)
pir        = Pin(14, Pin.IN)
dht_sensor = dht.DHT22(Pin(4))
gps        = UART(2, 115200)  # NEO-M8L @ 115200 bps (UBX protocol)

# ── Solicitar NAV-PVT al GPS NEO-M8L (mensaje UBX con posición) ──────────
# Protocolo UBX binario para NEO-M8L @ 115200 bps
UBX_NAV_PVT_REQ = bytes([
    0xB5, 0x62,        # Header
    0x01, 0x07,        # NAV-PVT
    0x00, 0x00,        # Sin payload (es un poll)
    0x08, 0x19         # Checksum
])

def blink(n=1):
    for _ in range(n):
        led.value(1); time.sleep(0.1)
        led.value(0); time.sleep(0.1)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        for _ in range(15):
            if wlan.isconnected():
                print("[WiFi] Conectado:", wlan.ifconfig()[0])
                blink(3)
                return True
            time.sleep(1)
    return wlan.isconnected()

def detectar_movimiento(duracion=2000):
    inicio = time.ticks_ms()
    mov = 0
    while time.ticks_diff(time.ticks_ms(), inicio) < duracion:
        if pir.value(): mov = 1
        time.sleep_ms(100)
    print("[PIR] Movimiento:", mov)
    return mov

def leer_temp():
    try:
        dht_sensor.measure()
        t = dht_sensor.temperature()
        print(f"[DHT] {t}°C")
        return t
    except:
        print("[DHT] Error")
        return None

def parsear_ubx_pvt(buf):
    """
    Parsea mensaje UBX NAV-PVT (0x01 0x07) — longitud fija 92 bytes
    Protocolo nativo del GPS NEO-M8L
    Contiene lat/lon en grados * 1e-7
    Fix válido si gnssFixOk (bit 0 de flags) está activo
    """
    i = 0
    while i < len(buf) - 6:
        # Buscar header UBX: 0xB5 0x62
        if buf[i] == 0xB5 and buf[i+1] == 0x62:
            if i+6 > len(buf): break
            cls  = buf[i+2]
            mid  = buf[i+3]
            lng  = buf[i+4] | (buf[i+5] << 8)

            if cls == 0x01 and mid == 0x07 and lng == 92:
                if i + 6 + 92 > len(buf):
                    break
                payload = buf[i+6 : i+6+92]

                # flags en byte 21 — bit 0 = gnssFixOk
                flags = payload[21]
                if not (flags & 0x01):
                    print("[GPS] Sin fix UBX (gnssFixOk=0)")
                    return None, None

                # lat y lon en bytes 28-31 y 24-27 (int32, little-endian, *1e-7)
                lon_raw = int.from_bytes(payload[24:28], 'little', True)
                lat_raw = int.from_bytes(payload[28:32], 'little', True)

                # Validar rangos válidos: lat [-90, 90], lon [-180, 180]
                lat = round(lat_raw / 1e7, 6)
                lon = round(lon_raw / 1e7, 6)
                
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    print(f"[GPS] Coordenadas inválidas: lat={lat}, lon={lon}")
                    return None, None
                
                print(f"[GPS] ✓ Fix UBX: lat={lat}, lon={lon}")
                return lat, lon
        i += 1
    return None, None

def leer_gps(timeout=8000):
    # Pedir posición al GPS
    gps.write(UBX_NAV_PVT_REQ)
    time.sleep_ms(200)

    inicio = time.ticks_ms()
    buf = b""

    while time.ticks_diff(time.ticks_ms(), inicio) < timeout:
        if gps.any():
            buf += gps.read()  # MicroPython: read() sin argumentos
            lat, lon = parsear_ubx_pvt(buf)
            if lat is not None:
                return lat, lon
        time.sleep_ms(100)

    print("[GPS] Timeout sin fix")
    return None, None

def enviar(temp, mov, lat, lon):
    url = f"{SUPABASE_URL}/rest/v1/{TABLA}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    data = {"temperatura": temp, "movimiento": bool(mov),
            "latitud": lat, "longitud": lon}
    
    # Verificar WiFi
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("[HTTP] ✗ WiFi desconectado")
        return
    
    print(f"[HTTP] Enviando: temp={temp}, mov={mov}, lat={lat}, lon={lon}")
    try:
        r = urequests.post(url, headers=headers, data=ujson.dumps(data))
        print("[HTTP] ✓ Respuesta:", r.status_code)
        r.close()
        if r.status_code in (200, 201):
            blink(1)
        else:
            print("[HTTP] ✗ Error HTTP:", r.status_code)
    except Exception as e:
        print("[HTTP] ✗ Error:", e)

def main():
    print("=== PetFinder Smart Collar (UBX) ===")
    blink(3)
    conectar_wifi()

    while True:
        print("\n--- NUEVO CICLO ---")
        mov  = detectar_movimiento(2000)
        temp = leer_temp()
        if temp is None: temp = 0.0
        lat, lon = leer_gps(8000)
        print("[DATA]", temp, mov, lat, lon)
        if network.WLAN(network.STA_IF).isconnected():
            enviar(temp, mov, lat, lon)
        time.sleep(INTERVALO)

try:
    main()
except Exception as e:
    print("Error crítico:", e)
    time.sleep(5)
    machine.reset()