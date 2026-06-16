# ═══════════════════════════════════════════════════════════════
# DIAGNÓSTICO SIMPLE - Sin DNS
# ═══════════════════════════════════════════════════════════════

import network, urequests, time

print("\n" + "="*60)
print("DIAGNÓSTICO SIMPLE")
print("="*60)

# Conectar WiFi
print("\n[1] Conectando WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("ENTEL_HOGAR_2.4G_Plus", "123456789")

for i in range(15):
    if wlan.isconnected():
        config = wlan.ifconfig()
        print(f"    ✓ Conectado: {config[0]}")
        print(f"    Gateway: {config[3]}")
        break
    time.sleep(1)

if not wlan.isconnected():
    print("    ✗ WiFi no conectó")
    exit()

# Test 1: Ping a gateway (router local)
print("\n[2] Probando ping a router local (gateway)...")
try:
    # Crear socket ICMP
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.settimeout(2)
    sock.sendto(b"test", ("192.168.100.1", 0))
    print("    ✓ Router accesible")
except Exception as e:
    print(f"    ℹ️  No se puede hacer ping (ICMP bloqueado): {e}")

# Test 2: Simple GET a IP conocida (8.8.8.8 Google DNS)
print("\n[3] Intentando GET a Google DNS (8.8.8.8)...")
try:
    r = urequests.get("http://8.8.8.8/", timeout=3)
    print(f"    ✓ Funciona: {r.status_code}")
    r.close()
except Exception as e:
    print(f"    ✗ Error: {e}")

# Test 3: Simple GET a IP de Supabase (si podemos resolver)
print("\n[4] Intentando GET HTTP a 142.251.41.14 (Google)...")
try:
    r = urequests.get("http://142.251.41.14/", timeout=3)
    print(f"    ✓ Funciona: {r.status_code}")
    r.close()
except Exception as e:
    print(f"    ✗ Error: {e}")

# Test 4: Probar HTTP con host locales
print("\n[5] Probando request con Host header...")
try:
    r = urequests.get("http://142.251.41.14/", 
                     headers={"Host": "google.com"},
                     timeout=3)
    print(f"    ✓ Funciona: {r.status_code}")
    r.close()
except Exception as e:
    print(f"    ✗ Error: {e}")

print("\n" + "="*60)
print("CONCLUSIÓN:")
print("  Si todos los tests fallan → Router bloquea internet")
print("  Si algunos funcionan → Problema específico de DNS o HTTPS")
print("="*60)
