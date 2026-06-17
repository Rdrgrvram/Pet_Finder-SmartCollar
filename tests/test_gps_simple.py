# ═══════════════════════════════════════════════════════════════
# TEST GPS SIMPLIFICADO - Solo UART 2
# Prueba los 2 baudrates más comunes
# ═══════════════════════════════════════════════════════════════

from machine import UART
import time

print("\n" + "="*60)
print("GPS NEO-M8L - TEST UART 2 (Baudrate check)")
print("="*60)

# Test 1: 9600 bps (default de muchos GPS)
print("\n[1/2] Probando UART 2 @ 9600 bps (5 segundos)...\n")
try:
    gps = UART(2, baudrate=9600, tx=16, rx=17, rxbuf=512)
    inicio = time.time()
    datos_9600 = False
    
    while time.time() - inicio < 5:
        if gps.any():
            data = gps.read(256)
            print(f"✓ DATOS @ 9600 bps: {data[:50]}")
            datos_9600 = True
            break
        time.sleep(0.1)
    
    if not datos_9600:
        print("✗ Sin datos @ 9600 bps")
    
    gps.deinit()
except Exception as e:
    print(f"✗ Error: {e}")
    datos_9600 = False

time.sleep(1)

# Test 2: 38400 bps (NEO-M8L configurado)
print("\n[2/2] Probando UART 2 @ 38400 bps (5 segundos)...\n")
try:
    gps = UART(2, baudrate=38400, tx=16, rx=17, rxbuf=512)
    inicio = time.time()
    datos_38400 = False
    
    while time.time() - inicio < 5:
        if gps.any():
            data = gps.read(256)
            print(f"✓ DATOS @ 38400 bps: {data[:50]}")
            datos_38400 = True
            break
        time.sleep(0.1)
    
    if not datos_38400:
        print("✗ Sin datos @ 38400 bps")
    
    gps.deinit()
except Exception as e:
    print(f"✗ Error: {e}")
    datos_38400 = False

# Resumen
print("\n" + "="*60)
print("RESULTADO")
print("="*60)

if datos_9600 or datos_38400:
    if datos_9600:
        print("\n✓✓✓ ¡EL GPS ESTÁ FUNCIONANDO @ 9600 bps!")
        print("\nUSA: main.py (o modifica main_fixed.py a 9600 bps)")
    if datos_38400:
        print("\n✓✓✓ ¡EL GPS ESTÁ FUNCIONANDO @ 38400 bps!")
        print("\nUSA: main_fixed.py")
    
    print("\n⚠️  IMPORTANTE:")
    print("   El GPS NECESITA SATÉLITES para obtener coordenadas")
    print("   • Lleva el ESP32 AFUERA")
    print("   • Espera 30-60 segundos (cold start)")
    print("   • Si estás en interior, NO funcionará")

else:
    print("\n✗✗✗ EL GPS NO ESTÁ ENVIANDO DATOS")
    print("\nVerifica:")
    print("   • Conexión TX (GPS) ↔ GPIO 17 (ESP32)")
    print("   • Conexión RX (GPS) ↔ GPIO 16 (ESP32)")
    print("   • Alimentación 3.3V y GND")
    print("   • LED rojo del GPS está encendido?")
    print("   • GPS está soldado correctamente?")

print("\n")
