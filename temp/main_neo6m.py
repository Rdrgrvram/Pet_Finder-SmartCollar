# ═══════════════════════════════════════════════════════════════
# MAIN CON NEO-6M (NMEA @ 9600 BPS)
# ═══════════════════════════════════════════════════════════════

from machine import UART, Pin
import network, urequests, ujson, time, machine
import dht

# ── Config ──────────────────────────────────────────────────────
WIFI_SSID     = "Redmi Rodri S"
WIFI_PASSWORD = "123456789"
SUPABASE_URL  = "https://kjuoamogxpplpyaseeat.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqdW9hbW9neHBwbHB5YXNlZWF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3OTU1NDUsImV4cCI6MjA5MjM3MTU0NX0.ty8SNcnELPCKk43qoRJft4-8IVQz6GrSouoX4T188CQ"
TABLA         = "lecturas_collar"
INTERVALO     = 5

# ── Hardware ─────────────────────────────────────────────────────
led        = Pin(2,  Pin.OUT)
pir        = Pin(14, Pin.IN)
dht_sensor = dht.DHT22(Pin(4))
gps        = UART(2, 9600)  # NEO-6M @ 9600 bps (NMEA por defecto)

def blink(n=1):
    for _ in range(n):
        led.value(1); time.sleep(0.1)
        led.value(0); time.sleep(0.1)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print(f"[WiFi] Activo: {wlan.active()}")
    
    if not wlan.isconnected():
        print(f"[WiFi] Conectando a {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        for i in range(15):
            if wlan.isconnected():
                print("[WiFi] ✓ Conectado:", wlan.ifconfig()[0])
                blink(3)
                return True
            print(f"[WiFi] Esperando... ({i+1}/15)")
            time.sleep(1)
        
        print("[WiFi] ✗ Timeout - no conectó")
        return False
    else:
        print("[WiFi] ✓ Ya conectado")
        return True

def detectar_movimiento(duracion=2000):
    inicio = time.ticks_ms()
    mov = 0
    while time.ticks_diff(time.ticks_ms(), inicio) < duracion:
        if pir.value():
            mov = 1
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

def parsear_nmea(linea):
    """
    Parsea sentencia NMEA GPRMC
    Formato: $GPRMC,hhmmss.ss,A,llll.ll,N,yyyyy.yy,E,x.x,x.x,ddmmyy,x.x,E,A*hh
    """
    try:
        if not linea.startswith(b"$GPRMC"):
            return None, None
        
        linea = linea.decode('utf-8').strip()
        partes = linea.split(',')
        
        if len(partes) < 10:
            return None, None
        
        # Verificar que tenga fix (A = válido)
        status = partes[2]
        if status != 'A':
            print("[GPS] Sin fix NMEA (status != A)")
            return None, None
        
        # Parsear latitud (formato: ddmm.mmmm)
        lat_str = partes[3]
        lat_dir = partes[4]
        
        # Parsear longitud (formato: dddmm.mmmm)
        lon_str = partes[5]
        lon_dir = partes[6]
        
        if not lat_str or not lon_str:
            return None, None
        
        # Convertir lat: dd + mm.mmmm / 60
        lat_deg = float(lat_str[:2])
        lat_min = float(lat_str[2:])
        lat = lat_deg + lat_min / 60.0
        if lat_dir == 'S':
            lat = -lat
        
        # Convertir lon: ddd + mm.mmmm / 60
        lon_deg = float(lon_str[:3])
        lon_min = float(lon_str[3:])
        lon = lon_deg + lon_min / 60.0
        if lon_dir == 'W':
            lon = -lon
        
        lat = round(lat, 6)
        lon = round(lon, 6)
        
        # Validar rangos
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            print(f"[GPS] Coordenadas fuera de rango: lat={lat}, lon={lon}")
            return None, None
        
        print(f"[GPS] ✓ NMEA válido: lat={lat}, lon={lon}")
        return lat, lon
    except Exception as e:
        print(f"[GPS] Error parseo NMEA: {e}")
        return None, None

def leer_gps(timeout=8000):
    """Lee GPS NMEA hasta obtener GPRMC válido"""
    inicio = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), inicio) < timeout:
        if gps.any():
            linea = gps.readline()
            
            if linea:
                lat, lon = parsear_nmea(linea)
                if lat is not None:
                    return lat, lon
        
        time.sleep_ms(50)
    
    print("[GPS] Timeout sin fix")
    return None, None

def enviar(temp, mov, lat, lon):
    """Envía datos a Supabase"""
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("[HTTP] ✗ WiFi desconectado, no envío")
        return
    
    url = f"{SUPABASE_URL}/rest/v1/{TABLA}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "temperatura": temp, 
        "movimiento": bool(mov),
        "latitud": lat, 
        "longitud": lon
    }
    
    print(f"[HTTP] POST a Supabase...")
    try:
        r = urequests.post(url, headers=headers, data=ujson.dumps(data), timeout=5)
        print(f"[HTTP] ✓ Status: {r.status_code}")
        r.close()
        if r.status_code in (200, 201):
            blink(1)
            print("[HTTP] ✓ Datos guardados")
        else:
            print(f"[HTTP] ✗ Error HTTP {r.status_code}")
    except Exception as e:
        print(f"[HTTP] ✗ Error: {e}")

def main():
    print("=== PetFinder Smart Collar (NEO-6M NMEA) ===")
    blink(3)
    
    wifi_conectado = conectar_wifi()
    print(f"[INIT] WiFi conectado: {wifi_conectado}\n")

    while True:
        print("\n--- NUEVO CICLO ---")
        mov  = detectar_movimiento(2000)
        temp = leer_temp()
        if temp is None: 
            temp = 0.0
        lat, lon = leer_gps(8000)
        print("[DATA]", temp, mov, lat, lon)
        
        enviar(temp, mov, lat, lon)
        
        time.sleep(INTERVALO)

try:
    main()
except Exception as e:
    print("Error crítico:", e)
    time.sleep(5)
    machine.reset()
