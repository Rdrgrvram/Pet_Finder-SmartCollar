# ═══════════════════════════════════════════════════════════════
# MAIN CON GPS SIMULADO - Para testing en casa
# Funciona igual que main_nmea_9600.py pero con datos GPS inventados
# ═══════════════════════════════════════════════════════════════

from machine import Pin
import network, urequests, ujson, time, machine
import dht
import random

# ── Config ──────────────────────────────────────────────────────
WIFI_SSID     = "ENTEL_HOGAR_5G"
WIFI_PASSWORD = "123456789"
SUPABASE_URL  = "https://kjuoamogxpplpyaseeat.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqdW9hbW9neHBwbHB5YXNlZWF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3OTU1NDUsImV4cCI6MjA5MjM3MTU0NX0.ty8SNcnELPCKk43qoRJft4-8IVQz6GrSouoX4T188CQ"
TABLA         = "lecturas_collar"
INTERVALO     = 5  # Reducido a 5 segundos para testing rápido

# ── Hardware ─────────────────────────────────────────────────────
led        = Pin(2,  Pin.OUT)
pir        = Pin(14, Pin.IN)
dht_sensor = dht.DHT22(Pin(4))

# Datos GPS simulados (Cochabamba, Bolivia + variación aleatoria)
GPS_SIMULADO = {
    "lat_base": -17.3895,  # Cochabamba
    "lon_base": -66.1568,
    "lat_var": 0.0001,     # Variación pequeña (±10 metros)
    "lon_var": 0.0001,
}

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

def leer_gps_simulado():
    """
    Genera datos GPS simulados con pequeña variación.
    En una app real, leerías del UART. Aquí simulamos para testing.
    """
    # Generar coordenadas con pequeña variación aleatoria
    lat = GPS_SIMULADO["lat_base"] + (random.random() - 0.5) * GPS_SIMULADO["lat_var"]
    lon = GPS_SIMULADO["lon_base"] + (random.random() - 0.5) * GPS_SIMULADO["lon_var"]
    
    print(f"[GPS] ✓ Simulado: lat={lat:.6f}, lon={lon:.6f}")
    return round(lat, 6), round(lon, 6)

def enviar(temp, mov, lat, lon):
    """Envía datos a Supabase"""
    # Verificar WiFi primero
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
    print("=== PetFinder Smart Collar (GPS SIMULADO - Testing) ===")
    print("⚠️  Nota: Usando GPS simulado. En producción, llevalo afuera.")
    blink(3)
    
    wifi_conectado = conectar_wifi()
    print(f"[INIT] WiFi conectado: {wifi_conectado}\n")

    while True:
        print("\n--- NUEVO CICLO ---")
        mov  = detectar_movimiento(2000)
        temp = leer_temp()
        if temp is None: 
            temp = 0.0
        lat, lon = leer_gps_simulado()  # GPS simulado
        print("[DATA]", temp, mov, lat, lon)
        
        # Enviar siempre (enviar() mismo verifica WiFi)
        enviar(temp, mov, lat, lon)
        
        time.sleep(INTERVALO)

try:
    main()
except Exception as e:
    print("Error crítico:", e)
    time.sleep(5)
    machine.reset()
