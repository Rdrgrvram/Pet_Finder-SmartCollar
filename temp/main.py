import network, urequests, ujson, time, machine
from machine import Pin, UART
import dht

WIFI_SSID     = "GpsFi"
WIFI_PASSWORD = "juiop123"
SUPABASE_URL  = "https://kjuoamogxpplpyaseeat.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqdW9hbW9neHBwbHB5YXNlZWF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3OTU1NDUsImV4cCI6MjA5MjM3MTU0NX0.ty8SNcnELPCKk43qoRJft4-8IVQz6GrSouoX4T188CQ"
TABLA         = "lecturas_collar"
INTERVALO     = 10

led        = Pin(2, Pin.OUT)
pir        = Pin(14, Pin.IN)
dht_sensor = dht.DHT22(Pin(4))
gps        = UART(2, baudrate=38400, tx=16, rx=17)  # ← NEO-M8L @ 38400 bps

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
            if wlan.isconnected():  # ← sin el + 
                print("[WiFi] Conectado:", wlan.ifconfig()[0])
                blink(3)
                return True
            time.sleep(1)
    return wlan.isconnected()

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

def convertir(raw, dir):
    if not raw: return None
    if len(raw) > 7:
        g = int(raw[:3]); m = float(raw[3:])
    else:
        g = int(raw[:2]); m = float(raw[2:])
    d = g + m / 60
    if dir in ["S", "W"]: d = -d
    return round(d, 6)

def leer_gps(timeout=8000):
    inicio = time.ticks_ms()
    buf = b""
    while time.ticks_diff(time.ticks_ms(), inicio) < timeout:
        if gps.any():
            buf += gps.read()
            while b"\n" in buf:
                linea, buf = buf.split(b"\n", 1)
                try:
                    txt = linea.decode().strip()
                    if txt.startswith("$GPRMC") or txt.startswith("$GNRMC"):
                        p = txt.split(",")
                        if len(p) > 6 and p[2] == "A":
                            lat = convertir(p[3], p[4])
                            lon = convertir(p[5], p[6])
                            print("[GPS] OK:", lat, lon)
                            return lat, lon
                except:
                    pass
        time.sleep_ms(50)
    print("[GPS] Sin fix")
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
    try:
        r = urequests.post(url, headers=headers, data=ujson.dumps(data))
        print("[HTTP]", r.status_code)
        r.close()
        if r.status_code in (200, 201):
            blink(1)
    except Exception as e:
        print("[ERROR]", e)

def main():
    print("=== PetFinder Smart Collar ===")
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