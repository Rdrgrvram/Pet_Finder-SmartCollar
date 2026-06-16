# ═══════════════════════════════════════════════════════════════
# TEST GPS - Diagnóstico de conexión UART
# Prueba si el GPS está enviando datos en cualquier baudrate
# ═══════════════════════════════════════════════════════════════

from machine import UART
import time

def test_uart_raw(uart_num, baudrate):
    """Lee datos brutos del UART sin parsear"""
    print(f"\n{'='*50}")
    print(f"UART {uart_num} @ {baudrate} bps")
    print('='*50)
    
    try:
        gps = UART(uart_num, baudrate=baudrate, tx=16, rx=17, rxbuf=512)
        print("✓ UART inicializado correctamente")
        print(f"Leyendo durante 3 segundos...\n")
        
        inicio = time.time()
        datos_recibidos = False
        
        while time.time() - inicio < 3:
            if gps.any():
                datos = gps.read(256)
                print(f"Datos recibidos ({len(datos)} bytes):")
                print(f"  Raw: {datos}")
                print(f"  ASCII: {datos.decode('utf-8', errors='ignore')}")
                print()
                datos_recibidos = True
                time.sleep(0.5)  # Dar tiempo a más datos
            else:
                time.sleep(0.1)
        
        if not datos_recibidos:
            print("✗ No se recibieron datos")
        
        gps.deinit()
        return datos_recibidos
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_uart_0():
    """Test UART 0 (Si está disponible)"""
    return test_uart_raw(0, 9600)

def test_uart_1():
    """Test UART 1"""
    return test_uart_raw(1, 9600)

def test_uart_2_9600():
    """Test UART 2 @ 9600 bps (baudrate por defecto)"""
    return test_uart_raw(2, 9600)

def test_uart_2_38400():
    """Test UART 2 @ 38400 bps (configured for NEO-M8L)"""
    return test_uart_raw(2, 38400)

def test_uart_2_115200():
    """Test UART 2 @ 115200 bps (algunos GPS usan esto)"""
    return test_uart_raw(2, 115200)

def main():
    print("\n" + "╔" + "="*48 + "╗")
    print("║" + " "*12 + "GPS NEO-M8L - TEST UART" + " "*13 + "║")
    print("╚" + "="*48 + "╝")
    
    print("\nEste script prueba todos los UART y baudrates posibles.")
    print("Si el GPS está conectado, verás datos AQUÍ.\n")
    
    resultados = {}
    
    # Probar diferentes UART y baudrates
    print("Probando UART 0 @ 9600 bps...")
    resultados['UART 0 @ 9600'] = test_uart_0()
    time.sleep(1)
    
    print("\n\nProbando UART 1 @ 9600 bps...")
    resultados['UART 1 @ 9600'] = test_uart_1()
    time.sleep(1)
    
    print("\n\nProbando UART 2 @ 9600 bps...")
    resultados['UART 2 @ 9600'] = test_uart_2_9600()
    time.sleep(1)
    
    print("\n\nProbando UART 2 @ 38400 bps...")
    resultados['UART 2 @ 38400'] = test_uart_2_38400()
    time.sleep(1)
    
    print("\n\nProbando UART 2 @ 115200 bps...")
    resultados['UART 2 @ 115200'] = test_uart_2_115200()
    
    # Resumen
    print("\n\n" + "="*50)
    print("RESUMEN")
    print("="*50)
    
    for config, resultado in resultados.items():
        estado = "✓ DATOS RECIBIDOS" if resultado else "✗ Sin datos"
        print(f"{config:20} {estado}")
    
    # Diagnóstico
    print("\n" + "="*50)
    print("DIAGNÓSTICO")
    print("="*50)
    
    if any(resultados.values()):
        print("✓ ¡El GPS ESTÁ ENVIANDO DATOS!")
        print("\nProblemas posibles:")
        print("  • El GPS está dentro de casa (necesita satélites)")
        print("  • Lleva el ESP32 afuera para obtener fix")
        print("  • Espera 30-60 segundos (cold start)")
    else:
        print("✗ El GPS NO está enviando datos")
        print("\nVerifica:")
        print("  • Conexiones físicas (TX ↔ RX, VCC, GND)")
        print("  • ¿Tiene LED rojo el GPS? (power indicator)")
        print("  • ¿Está soldado correctamente?")
        print("  • ¿Antena GPS conectada?")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
