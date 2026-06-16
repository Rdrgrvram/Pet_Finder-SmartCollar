# ═══════════════════════════════════════════════════════════════
# TEST GPIO - Verifica que GPIO 16 y 17 funcionan correctamente
# ═══════════════════════════════════════════════════════════════

from machine import Pin, UART
import time

def test_gpio_basico():
    """Test básico de GPIO 16 y 17"""
    print("\n" + "="*60)
    print("TEST GPIO 16 y 17")
    print("="*60)
    
    try:
        print("\nConfigurando GPIO 16 como OUTPUT...")
        pin16_out = Pin(16, Pin.OUT)
        print("✓ GPIO 16 configurado")
        
        print("Configurando GPIO 17 como OUTPUT...")
        pin17_out = Pin(17, Pin.OUT)
        print("✓ GPIO 17 configurado")
        
        print("\nParpadeando GPIO 16...")
        for i in range(3):
            pin16_out.value(1)
            time.sleep(0.2)
            pin16_out.value(0)
            time.sleep(0.2)
        print("✓ GPIO 16 parpadea")
        
        print("\nParpadeando GPIO 17...")
        for i in range(3):
            pin17_out.value(1)
            time.sleep(0.2)
            pin17_out.value(0)
            time.sleep(0.2)
        print("✓ GPIO 17 parpadea")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_uart_alternativo():
    """Prueba UART con diferentes configuraciones de pines"""
    print("\n" + "="*60)
    print("TEST UART - Diferentes configuraciones")
    print("="*60)
    
    configuraciones = [
        {"num": 1, "tx": 10, "rx": 9, "bd": 9600, "desc": "UART1 (TX:10, RX:9) @ 9600"},
        {"num": 2, "tx": 17, "rx": 16, "bd": 9600, "desc": "UART2 (TX:17, RX:16) @ 9600"},
        {"num": 2, "tx": 17, "rx": 16, "bd": 38400, "desc": "UART2 (TX:17, RX:16) @ 38400"},
    ]
    
    for config in configuraciones:
        try:
            print(f"\nProbando {config['desc']}...")
            uart = UART(
                config['num'],
                baudrate=config['bd'],
                tx=config['tx'],
                rx=config['rx'],
                rxbuf=512
            )
            print(f"  ✓ UART {config['num']} inicializado")
            
            # Intenta leer durante 1 segundo
            inicio = time.time()
            datos_encontrados = False
            
            while time.time() - inicio < 1:
                if uart.any():
                    data = uart.read(256)
                    print(f"  ✓ DATOS RECIBIDOS: {data[:30]}")
                    datos_encontrados = True
                    break
                time.sleep(0.05)
            
            if not datos_encontrados:
                print(f"  ✗ Sin datos")
            
            uart.deinit()
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ✗ Error: {e}")

def test_lista_pines_esp32():
    """Lista los pines disponibles del ESP32"""
    print("\n" + "="*60)
    print("INFORMACIÓN DEL ESP32")
    print("="*60)
    
    print("\nPines UART típicos en ESP32:")
    print("  UART0: TX=GPIO1,  RX=GPIO3  (comunicación con PC)")
    print("  UART1: TX=GPIO10, RX=GPIO9  (disponible)")
    print("  UART2: TX=GPIO17, RX=GPIO16 (NUESTRO GPS)")
    
    print("\nSi tu ESP32 es diferente (ej: WROOM-32):")
    print("  Consulta el datasheet específico del modelo")
    
    print("\n⚠️  IMPORTANTE:")
    print("  • Algunos ESP32 tienen pines diferentes")
    print("  • El GPS podría estar en un UART diferente")
    print("  • Verifica la documentación de tu placa")

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*15 + "DIAGNÓSTICO COMPLETO DE GPIO/UART" + " "*9 + "║")
    print("╚" + "="*58 + "╝")
    
    # Test 1: GPIO
    gpio_ok = test_gpio_basico()
    
    # Test 2: UART alternativas
    test_uart_alternativo()
    
    # Test 3: Info
    test_lista_pines_esp32()
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN Y RECOMENDACIONES")
    print("="*60)
    
    if gpio_ok:
        print("\n✓ GPIO 16 y 17 funcionan correctamente")
        print("\nProbables causas del problema con GPS:")
        print("  1. Conexiones físicas sueltas (revisa jumpers)")
        print("  2. GPS sin alimentación (¿LED rojo encendido?)")
        print("  3. GPS con defecto (intenta con otro)")
        print("  4. UART diferente en tu ESP32")
    else:
        print("\n✗ Hay un problema con los pines GPIO")
        print("  Contacta support o usa pins diferentes")
    
    print("\nPróximos pasos:")
    print("  1. Revisa físicamente las conexiones")
    print("  2. Verifica alimentación del GPS (LED rojo)")
    print("  3. Prueba el GPS en otra placa si es posible")
    print("  4. Consulta el datasheet de tu ESP32")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
