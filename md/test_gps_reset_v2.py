# ═══════════════════════════════════════════════════════════════
# RESET GPS SIMPLIFICADO - Versión MicroPython compatible
# ═══════════════════════════════════════════════════════════════

from machine import UART, Pin
import time

def reset_gps_pin():
    """Reinicia el GPS usando pin de RESET"""
    print("\n[1] Intentando reset por PIN...")
    
    reset_pins = [12, 13, 15, 32, 33]
    
    for pin_num in reset_pins:
        try:
            print(f"    Probando GPIO {pin_num}...")
            reset_pin = Pin(pin_num, Pin.OUT)
            reset_pin.value(0)
            time.sleep(0.1)
            reset_pin.value(1)
            print(f"    ✓ Reset GPIO {pin_num} enviado")
            time.sleep(1)
            return True
        except:
            pass
    
    print("    ℹ️  No se encontró pin RESET")
    return False

def limpiar_uart():
    """Limpia el buffer UART"""
    print("\n[2] Limpiando buffer UART...")
    
    try:
        gps = UART(2, 9600, tx=17, rx=16, rxbuf=512)
        
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
    
    RESET_CMD = bytes([
        0xB5, 0x62, 0x06, 0x04, 0x04, 0x00,
        0xFF, 0xFF, 0x00, 0x00, 0x0E, 0x46
    ])
    
    try:
        gps = UART(2, 9600, tx=17, rx=16, rxbuf=512)
        gps.write(RESET_CMD)
        print("    ✓ Reset enviado")
        time.sleep(3)
        gps.deinit()
        return True
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def verificar_respuesta():
    """Verifica respuesta en diferentes baudrates"""
    print("\n[4] Verificando respuesta GPS...")
    print("    Leyendo durante 15 segundos...\n")
    
    baudrates = [9600, 38400, 115200, 4800]
    
    for bd in baudrates:
        print(f"    @ {bd} bps: ", end="", flush=True)
        
        try:
            gps = UART(2, bd, tx=17, rx=16, rxbuf=512)
            
            inicio = time.ticks_ms()
            encontrado = False
            
            while time.ticks_diff(time.ticks_ms(), inicio) < 3000:
                if gps.any():
                    data = gps.read(256)
                    
                    # Buscar NMEA
                    if b"$GN" in data or b"$GP" in data:
                        print(f"✓ NMEA @ {bd}")
                        encontrado = True
                        break
                    # Buscar UBX
                    elif len(data) > 1 and data[0] == 0xB5 and data[1] == 0x62:
                        print(f"✓ UBX @ {bd}")
                        encontrado = True
                        break
                
                time.sleep(0.05)
            
            if not encontrado:
                print("✗")
            
            gps.deinit()
            time.sleep(0.2)
            
            if encontrado:
                return bd
        except Exception as e:
            print(f"E({e})")
    
    print("\n    ✗ Sin respuesta")
    return None

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*12 + "RESET COMPLETO DEL GPS NEO-M8L" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\nReseteando GPS...")
    
    # Ejecutar pasos
    reset_gps_pin()
    time.sleep(1)
    
    limpiar_uart()
    time.sleep(1)
    
    reset_por_software()
    time.sleep(2)
    
    baudrate = verificar_respuesta()
    
    # Resultado
    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)
    
    if baudrate:
        print(f"\n✓✓✓ ¡GPS FUNCIONA!")
        print(f"    Protocolo: NMEA")
        print(f"    Baudrate: {baudrate} bps")
        print(f"\n¿Próximo paso?")
        if baudrate == 9600:
            print("    Ejecuta: main_nmea_9600.py")
        else:
            print(f"    Modifica main_nmea_9600.py cambiar baudrate a {baudrate}")
    else:
        print("\n✗ GPS sigue sin responder después del reset")
        print("\n¿Qué probamos?")
        print("  1. GPS definitivamente está encendido (LED rojo)")
        print("  2. Reset por PIN y software ejecutados")
        print("  3. Buffer limpiado")
        print("\n¿Qué significa?")
        print("  • El GPS podría tener firmware especial/personalizado")
        print("  • El GPS podría estar defectuoso")
        print("  • Podría necesitar u-center (software u-blox)")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrumpido")
    except Exception as e:
        print(f"\nError: {e}")
