# ═══════════════════════════════════════════════════════════════
# RESET GPS - VERSIÓN ULTRA-SIMPLE
# Sin funciones de tiempo complicadas
# ═══════════════════════════════════════════════════════════════

from machine import UART, Pin
import time

print("\n" + "="*60)
print("RESET GPS NEO-M8L - VERSIÓN SIMPLE")
print("="*60)

# PASO 1: Reset por GPIO 12
print("\n[1] Reset por GPIO 12...")
try:
    reset_pin = Pin(12, Pin.OUT)
    reset_pin.value(0)
    time.sleep(0.1)
    reset_pin.value(1)
    print("    ✓ Reset enviado")
    time.sleep(1)
except:
    print("    ℹ️  GPIO 12 no disponible (normal)")

# PASO 2: Limpiar buffer
print("\n[2] Limpiando buffer UART...")
try:
    gps = UART(2, 9600)
    while gps.any():
        data = gps.read()
        if data:
            print(f"    Limpiando: {len(data)} bytes")
        time.sleep(0.1)
    print("    ✓ Buffer limpio")
    gps.deinit()
except Exception as e:
    print(f"    Error: {e}")

# PASO 3: Reset por UBX
print("\n[3] Reset por software...")
try:
    gps = UART(2, 9600)
    RESET = bytes([0xB5, 0x62, 0x06, 0x04, 0x04, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x0E, 0x46])
    gps.write(RESET)
    print("    ✓ Reset enviado")
    time.sleep(3)
    gps.deinit()
except Exception as e:
    print(f"    Error: {e}")

# PASO 4: Verificar respuesta
print("\n[4] Verificando GPS...")
print("    Probando baudrates...\n")

def probar_baudrate(baudrate):
    print(f"    @ {baudrate} bps: ", end="", flush=True)
    try:
        # Intentar destruir UART completamente
        try:
            gps_old = UART(2)
            gps_old.deinit()
        except:
            pass
        
        time.sleep(0.5)
        
        # Crear nuevo UART
        gps = UART(2, baudrate)
        time.sleep(0.5)
        
        # Leer durante 3 segundos
        for i in range(30):
            if gps.any():
                data = gps.read()
                
                if data:
                    # Buscar NMEA
                    if b"$GN" in data or b"$GP" in data:
                        print(f"✓ NMEA")
                        try:
                            gps.deinit()
                        except:
                            pass
                        return baudrate
                    # Buscar UBX
                    elif len(data) > 1 and data[0] == 0xB5 and data[1] == 0x62:
                        print(f"✓ UBX")
                        try:
                            gps.deinit()
                        except:
                            pass
                        return baudrate
            
            time.sleep(0.1)
        
        print("✗")
        try:
            gps.deinit()
        except:
            pass
        time.sleep(0.5)
        return None
    except Exception as e:
        print(f"Error: {e}")
        try:
            gps.deinit()
        except:
            pass
        time.sleep(0.5)
        return None

encontrado_baudrate = None
for bd in [9600, 38400, 115200]:
    resultado = probar_baudrate(bd)
    if resultado:
        encontrado_baudrate = resultado
        break

# RESULTADO
print("\n" + "="*60)
print("RESULTADO")
print("="*60)

if encontrado_baudrate:
    print(f"\n✓✓✓ ¡GPS ENCONTRADO!")
    print(f"    Baudrate: {encontrado_baudrate} bps")
    print(f"\n    Ejecuta: main_nmea_{encontrado_baudrate}.py")
else:
    print("\n✗ GPS sin respuesta")
    print("\n¿Qué pasó?")
    print("  1. GPIO 12 reset fue enviado")
    print("  2. Buffer UART fue limpiado")
    print("  3. Reset UBX fue enviado")
    print("  4. Se buscó en 3 baudrates")
    print("\nProbable causa:")
    print("  • GPS defectuoso o firmware corrupto")
    print("  • Necesita software u-center para resetear")
    print("  • Contactar soporte u-blox")

print("\n")
