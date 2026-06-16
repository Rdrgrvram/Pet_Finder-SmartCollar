# ═══════════════════════════════════════════════════════════════
# PRUEBA GPS A 115200 BPS
# ═══════════════════════════════════════════════════════════════

from machine import UART, Pin
import time

print("\n" + "="*60)
print("PRUEBA GPS NEO-M8L @ 115200 BPS")
print("="*60)

# Reset GPIO 12
print("\n[1] Reset por GPIO 12...")
try:
    reset_pin = Pin(12, Pin.OUT)
    reset_pin.value(0)
    time.sleep(0.1)
    reset_pin.value(1)
    print("    ✓ Reset enviado")
    time.sleep(1)
except:
    print("    ℹ️  GPIO 12 no disponible")

# Crear UART a 115200
print("\n[2] Abriendo UART @ 115200 bps...")
try:
    gps = UART(2, 115200)
    print("    ✓ UART iniciado")
    time.sleep(1)
except Exception as e:
    print(f"    ✗ Error: {e}")
    exit()

# Limpiar buffer inicial
print("\n[3] Limpiando buffer...")
while gps.any():
    data = gps.read()
    time.sleep(0.05)
print("    ✓ Buffer limpio")

# Enviar reset UBX
print("\n[4] Enviando reset UBX...")
try:
    RESET = bytes([0xB5, 0x62, 0x06, 0x04, 0x04, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x0E, 0x46])
    gps.write(RESET)
    print("    ✓ Reset enviado")
    time.sleep(3)
except Exception as e:
    print(f"    ✗ Error: {e}")

# Leer respuesta
print("\n[5] Buscando respuesta (5 segundos)...\n")
encontrado = False
for i in range(50):
    if gps.any():
        data = gps.read()
        if data:
            print(f"    [{i}] Recibido {len(data)} bytes")
            
            # Buscar NMEA
            if b"$GN" in data or b"$GP" in data:
                print("    ✓✓✓ ¡NMEA ENCONTRADO!")
                encontrado = True
                break
            # Buscar UBX
            elif len(data) > 1 and data[0] == 0xB5 and data[1] == 0x62:
                print("    ✓✓✓ ¡UBX ENCONTRADO!")
                encontrado = True
                break
            else:
                # Mostrar primeros bytes
                print(f"         Primeros bytes: {data[:20]}")
    
    time.sleep(0.1)

print("\n" + "="*60)
if encontrado:
    print("✓✓✓ GPS FUNCIONA EN 115200 BPS")
else:
    print("✗ GPS NO RESPONDE EN 115200 BPS")
print("="*60 + "\n")
