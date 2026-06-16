# ═══════════════════════════════════════════════════════════════
# TEST GPS COMPLETO - Todos los baudrates y configuraciones
# ═══════════════════════════════════════════════════════════════

from machine import UART
import time

def test_todos_baudrates():
    """Prueba TODOS los baudrates comunes"""
    
    baudrates = [4800, 9600, 19200, 38400, 57600, 115200, 230400]
    
    print("\n" + "="*60)
    print("PROBANDO TODOS LOS BAUDRATES")
    print("="*60)
    print("\nProbando UART 2 (TX:17, RX:16) con todos los baudrates...")
    print("(Esto puede tomar ~1 minuto)\n")
    
    datos_encontrados = False
    
    for bd in baudrates:
        print(f"[{bd:6} bps] Leyendo... ", end="", flush=True)
        
        try:
            gps = UART(2, baudrate=bd, tx=17, rx=16, rxbuf=512)
            
            inicio = time.time()
            while time.time() - inicio < 1:
                if gps.any():
                    data = gps.read(512)
                    print(f"\n           ✓✓✓ DATOS ENCONTRADOS!!! ✓✓✓")
                    print(f"           Primeros 60 bytes: {data[:60]}")
                    print(f"           Baudrate correcto: {bd} bps\n")
                    datos_encontrados = True
                    gps.deinit()
                    return bd
                time.sleep(0.05)
            
            print("✗")
            gps.deinit()
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.2)
    
    return None

def test_tx_rx_invertido():
    """Prueba con TX/RX invertidos (por si está conectado al revés)"""
    
    print("\n" + "="*60)
    print("PRUEBA TX/RX INVERTIDO")
    print("="*60)
    print("\nA veces los cables están conectados al revés.")
    print("Probando con TX:16, RX:17 (invertido)...\n")
    
    baudrates = [9600, 38400, 115200]
    
    for bd in baudrates:
        print(f"[{bd:6} bps] Leyendo (invertido)... ", end="", flush=True)
        
        try:
            gps = UART(2, baudrate=bd, tx=16, rx=17, rxbuf=512)
            
            inicio = time.time()
            while time.time() - inicio < 1:
                if gps.any():
                    data = gps.read(512)
                    print(f"\n           ✓✓✓ ¡CABLES ESTÁN INVERTIDOS! ✓✓✓")
                    print(f"           Datos: {data[:60]}")
                    print(f"           Baudrate: {bd} bps\n")
                    print("           CAMBIA LA CONEXIÓN:")
                    print("           GPS TX → GPIO 16")
                    print("           GPS RX → GPIO 17\n")
                    gps.deinit()
                    return True
                time.sleep(0.05)
            
            print("✗")
            gps.deinit()
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.2)
    
    return False

def despertar_gps_ubx():
    """Intenta despertar el GPS enviando comandos UBX"""
    
    print("\n" + "="*60)
    print("INTENTANDO DESPERTAR GPS (Comando UBX)")
    print("="*60)
    
    print("\nEnviando comando NAV-PVT al GPS...\n")
    
    # Comando UBX NAV-PVT
    UBX_NAV_PVT_REQ = bytes([0xB5, 0x62, 0x01, 0x07, 0x00, 0x00, 0x08, 0x19])
    
    try:
        gps = UART(2, baudrate=38400, tx=17, rx=16, rxbuf=512)
        
        print("Enviando comando UBX...")
        gps.write(UBX_NAV_PVT_REQ)
        time.sleep(0.5)
        
        inicio = time.time()
        while time.time() - inicio < 3:
            if gps.any():
                data = gps.read(512)
                print(f"✓ Respuesta recibida: {data[:60]}")
                gps.deinit()
                return True
            time.sleep(0.1)
        
        print("✗ Sin respuesta")
        gps.deinit()
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "GPS NEO-M8L - DIAGNÓSTICO AVANZADO" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\nEste script busca el problema usando:")
    print("  1. Todos los baudrates posibles")
    print("  2. TX/RX invertido")
    print("  3. Comando UBX para despertar GPS")
    
    # Test 1: Todos los baudrates
    baudrate_correcto = test_todos_baudrates()
    
    if baudrate_correcto:
        print(f"\n✓✓✓ ENCONTRADO: GPS @ {baudrate_correcto} bps")
        return
    
    time.sleep(1)
    
    # Test 2: TX/RX invertido
    invertido = test_tx_rx_invertido()
    
    if invertido:
        print("\n✓✓✓ SOLUCIÓN: Invierte los cables TX/RX")
        return
    
    time.sleep(1)
    
    # Test 3: Despertar
    despertar_gps_ubx()
    
    # Resumen
    print("\n" + "="*60)
    print("DIAGNÓSTICO FINAL")
    print("="*60)
    
    if baudrate_correcto or invertido:
        print("\n✓ ¡PROBLEMA RESUELTO!")
    else:
        print("\n✗ No se encontraron datos en ninguna configuración")
        print("\nProbables causas:")
        print("  1. GPS tiene defecto (no envía datos)")
        print("  2. Pines GPIO 16/17 están dañados")
        print("  3. Conexión del cable muy sucia/oxidada")
        print("  4. Falta soldadura en los pines")
        print("\nRecomendación: Prueba el GPS en otra placa o con otro cable")
    
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
