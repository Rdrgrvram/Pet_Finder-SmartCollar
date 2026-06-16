# ═══════════════════════════════════════════════════════════════
# RESET AGRESIVO DEL GPS - Limpia buffer y reinicia
# ═══════════════════════════════════════════════════════════════

from machine import UART, Pin
import time

def reset_gps_pin():
    """Reinicia el GPS usando pin de RESET (si existe)"""
    print("\n[1] Intentando reset por PIN...")
    
    # Algunos GPS NEO-M8L tienen pin de reset
    # Probar diferentes pines
    reset_pins = [12, 13, 15, 32, 33]
    
    for pin_num in reset_pins:
        try:
            print(f"    Probando GPIO {pin_num}...")
            reset_pin = Pin(pin_num, Pin.OUT)
            reset_pin.value(0)  # LOW
            time.sleep(0.1)
            reset_pin.value(1)  # HIGH
            print(f"    ✓ Reset GPIO {pin_num} enviado")
            time.sleep(1)
            return True
        except:
            pass
    
    print("    ℹ️  No se encontró pin RESET (normal)")
    return False

def limpiar_uart():
    """Limpia el buffer UART"""
    print("\n[2] Limpiando buffer UART...")
    
    try:
        gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
        
        # Leer todo lo que hay en el buffer
        veces = 0
        while gps.any() and veces < 10:
            data = gps.read(256)
            print(f"    Limpiando: {len(data)} bytes")
            time.sleep(0.1)
            veces += 1
        
        print("    ✓ Buffer limpio")
        gps.deinit()
        return True
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def reset_por_software():
    """Reset software UBX"""
    print("\n[3] Reset por software (UBX)...")
    
    # Comando de reset firmware del GPS
    RESET_CMD = bytes([
        0xB5, 0x62,  # Header
        0x06, 0x04,  # CFG-RST
        0x04, 0x00,  # Longitud
        0xFF,        # Flags: reset hard
        0xFF, 0x00, 0x00,
        0x0E, 0x46   # Checksum
    ])
    
    try:
        gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
        gps.write(RESET_CMD)
        print("    ✓ Reset enviado")
        time.sleep(3)
        gps.deinit()
        return True
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def cambiar_a_nmea():
    """Cambia GPS a protocolo NMEA puro"""
    print("\n[4] Configurando GPS a NMEA...")
    
    # Comando: Cambiar a protocolo NMEA
    NMEA_CONFIG = bytes([
        0xB5, 0x62,        # Header UBX
        0x06, 0x00,        # CFG-PRT (puerto)
        0x14, 0x00,        # Longitud
        0x01,              # Puerto UART1
        0x00,              # Reserved
        0x00, 0x00,        # TX Ready
        0xE0, 0x08, 0x00, 0x00,  # Baudrate 2400 (cambiar después)
        0x07,              # Databits
        0x00,              # Parity
        0x00,              # Stopbits
        0x00, 0x00,        # CTS/RTS
        0x00, 0x00,        # Reserved
        0x00, 0x00,
        0x7E, 0x55         # Checksum
    ])
    
    try:
        gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
        gps.write(NMEA_CONFIG)
        print("    ✓ Configuración enviada")
        time.sleep(1)
        gps.deinit()
        return True
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def verificar_respuesta():
    """Verifica si el GPS responde después del reset"""
    print("\n[5] Verificando respuesta GPS...")
    print("    Leyendo durante 30 segundos...\n")
    
    baudrates = [9600, 38400, 115200, 4800, 19200]
    
    for bd in baudrates:
        print(f"    @ {bd} bps:", end="", flush=True)
        
        try:
            gps = UART(2, baudrate=bd, tx=17, rx=16, rxbuf=512)
            
            inicio = time.time()
            encontrado = False
            
            while time.time() - inicio < 3:
                if gps.any():
                    data = gps.read(256)
                    
                    # Buscar patrones
                    if b"$GN" in data or b"$GP" in data:
                        print(f" ✓ NMEA @ {bd}")
                        encontrado = True
                        break
                    elif data[0:2] == b'\xb5\x62':
                        print(f" ✓ UBX @ {bd}")
                        encontrado = True
                        break
                
                time.sleep(0.05)
            
            if not encontrado:
                print(" ✗", end="", flush=True)
            
            gps.deinit()
            time.sleep(0.2)
            
            if encontrado:
                return bd
        except:
            print(" E", end="", flush=True)
    
    print("\n    ✗ Sin respuesta en ningún baudrate")
    return None

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*12 + "RESET COMPLETO DEL GPS NEO-M8L" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\nEste script resetea completamente el GPS")
    print("y lo configura a NMEA puro.\n")
    
    # Paso 1: Reset por pin (si existe)
    reset_gps_pin()
    time.sleep(1)
    
    # Paso 2: Limpiar buffer
    limpiar_uart()
    time.sleep(1)
    
    # Paso 3: Reset por software
    reset_por_software()
    time.sleep(2)
    
    # Paso 4: Configurar NMEA
    cambiar_a_nmea()
    time.sleep(1)
    
    # Paso 5: Verificar
    baudrate_ok = verificar_respuesta()
    
    # Resultado
    print("\n" + "="*60)
    print("RESULTADO")
    print("="*60)
    
    if baudrate_ok:
        print(f"\n✓✓✓ ¡GPS RESETADO CORRECTAMENTE!")
        print(f"    Baudrate: {baudrate_ok} bps")
        print(f"\nAhora usa:")
        if baudrate_ok == 9600:
            print("    → main_nmea_9600.py")
        else:
            print(f"    → Crea main_nmea_{baudrate_ok}.py")
    else:
        print("\n✗✗✗ GPS sigue sin responder")
        print("\nÚltimas opciones:")
        print("  1. Busca datasheet del GPS (puede tener firmware especial)")
        print("  2. Intenta resetear con u-center (software u-blox)")
        print("  3. Comprueba que la antena esté bien conectada")
        print("  4. El GPS podría estar defectuoso")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido")
    except Exception as e:
        print(f"\nError: {e}")

