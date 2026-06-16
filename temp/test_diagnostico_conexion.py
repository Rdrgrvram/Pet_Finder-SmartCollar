# ═══════════════════════════════════════════════════════════════
# DIAGNÓSTICO CONEXIÓN - Verificar qué funciona
# ═══════════════════════════════════════════════════════════════

import network, urequests, socket, time

print("\n" + "="*60)
print("DIAGNÓSTICO DE CONEXIÓN")
print("="*60)

# Conectar WiFi
print("\n[1] Conectando WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("ENTEL_HOGAR_2.4G_Plus", "123456789")

for i in range(15):
    if wlan.isconnected():
        print(f"    ✓ Conectado: {wlan.ifconfig()[0]}")
        break
    time.sleep(1)

if not wlan.isconnected():
    print("    ✗ WiFi no conectó")
    exit()

# Test 1: Ping a DNS
print("\n[2] Probando resolución DNS (google.com)...")
try:
    ip = socket.gethostbyname("google.com")
    print(f"    ✓ google.com = {ip}")
except Exception as e:
    print(f"    ✗ Error DNS: {e}")

# Test 2: HTTP a servidor público
print("\n[3] Probando HTTP (httpbin.org)...")
try:
    r = urequests.get("http://httpbin.org/get", timeout=5)
    print(f"    ✓ HTTP funciona: {r.status_code}")
    r.close()
except Exception as e:
    print(f"    ✗ HTTP error: {e}")

# Test 3: HTTPS a servidor público
print("\n[4] Probando HTTPS (httpbin.org)...")
try:
    r = urequests.get("https://httpbin.org/get", timeout=5)
    print(f"    ✓ HTTPS funciona: {r.status_code}")
    r.close()
except Exception as e:
    print(f"    ✗ HTTPS error: {e}")

# Test 4: Resolver Supabase
print("\n[5] Probando Supabase DNS...")
try:
    ip = socket.gethostbyname("kjuoamogxpplpyaseeat.supabase.co")
    print(f"    ✓ Supabase resuelve a {ip}")
except Exception as e:
    print(f"    ✗ Error: {e}")

# Test 5: POST HTTP a httpbin
print("\n[6] Probando POST HTTP (httpbin.org)...")
try:
    r = urequests.post("http://httpbin.org/post", 
                       data='{"test": "data"}',
                       headers={"Content-Type": "application/json"},
                       timeout=5)
    print(f"    ✓ POST HTTP funciona: {r.status_code}")
    r.close()
except Exception as e:
    print(f"    ✗ POST HTTP error: {e}")

# Test 6: POST HTTPS a Supabase
print("\n[7] Probando POST HTTPS a Supabase...")
try:
    url = "https://kjuoamogxpplpyaseeat.supabase.co/rest/v1/lecturas_collar"
    headers = {
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqdW9hbW9neHBwbHB5YXNlZWF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3OTU1NDUsImV4cCI6MjA5MjM3MTU0NX0.ty8SNcnELPCKk43qoRJft4-8IVQz6GrSouoX4T188CQ",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqdW9hbW9neHBwbHB5YXNlZWF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3OTU1NDUsImV4cCI6MjA5MjM3MTU0NX0.ty8SNcnELPCKk43qoRJft4-8IVQz6GrSouoX4T188CQ",
        "Content-Type": "application/json"
    }
    r = urequests.post(url, 
                       data='{"temperatura": 25.5, "movimiento": true, "latitud": -17.389, "longitud": -66.156}',
                       headers=headers,
                       timeout=5)
    print(f"    ✓ POST Supabase funciona: {r.status_code}")
    r.close()
except Exception as e:
    print(f"    ✗ POST Supabase error: {e}")

print("\n" + "="*60)
