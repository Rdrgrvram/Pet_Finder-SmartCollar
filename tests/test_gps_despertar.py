# ═══════════════════════════════════════════════════════════════
# DESPERTAR GPS + BUSCAR DATOS VÁLIDOS
# ═══════════════════════════════════════════════════════════════

from machine import UART
import time

def despertar_gps_soft_reset():
    """Envía SoftReset al GPS NEO-M8L"""
    print("\n[1] Enviando SoftReset al GPS...")
    
    # Comando UBX: Soft reset
    UBX_RESET = bytes([
        0xB5, 0x62,        # Header
        0x06, 0x04,        # CFG-RST (reset)
        0x04, 0x00,        # Longitud payload
        0x00, 0x00, 0x02, 0x00,  # Soft reset
        0x0E, 0x46         # Checksum
    ])
    
    try:
        gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
        gps.write(UBX_RESET)
        print("   ✓ Comando enviado")
        time.sleep(1)
        gps.deinit()
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def despertar_gps_nav_pvt():
    """Solicita posición (NAV-PVT)"""
    print("\n[2] Enviando comando NAV-PVT...")
    
    UBX_NAV_PVT = bytes([
        0xB5, 0x62,        # Header
        0x01, 0x07,        # NAV-PVT
        0x00, 0x00,        # Sin payload
        0x08, 0x19         # Checksum
    ])
    
    try:
        gps = UART(2, baudrate=38400, tx=17, rx=16, rxbuf=512)
        gps.write(UBX_NAV_PVT)
        print("   ✓ Comando enviado")
        time.sleep(1)
        gps.deinit()
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def buscar_datos_validos():
    """Busca sentencias NMEA válidas"""
    print("\n[3] Buscando datos NMEA válidos...")
    print("    (Leyendo durante 5 segundos)\n")
    
    try:
        gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
        
        inicio = time.time()
        buf = b""
        nmea_encontradas = []
        
        while time.time() - inicio < 5:
            if gps.any():
                data = gps.read(256)
                buf += data
                
                # Buscar sentencias NMEA (empiezan con $)
                while b"$" in buf:
                    idx = buf.find(b"$")
                    siguiente = buf.find(b"$", idx + 1)
                    
                    if siguiente == -1:
                        siguiente = len(buf)
                    
                    sentencia = buf[idx:siguiente]
                    buf = buf[siguiente:]
                    
                    if sentencia.startswith(b"$GN") or sentencia.startswith(b"$GP"):
                        nmea_encontradas.append(sentencia)
                        print(f"    ✓ {sentencia.decode('utf-8', errors='ignore').strip()}")
            
            time.sleep(0.05)
        
        gps.deinit()
        
        if nmea_encontradas:
            print(f"\n    ✓✓✓ Encontradas {len(nmea_encontradas)} sentencias NMEA")
            return True
        else:
            print(f"    ✗ No se encontraron sentencias NMEA")
            return False
            
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*12 + "GPS NEO-M8L - DESPERTAR Y BUSCAR" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\nEl GPS está enviando datos pero en modo SLEEP.")
    print("Este script lo despertará y buscará sentencias válidas.\n")
    
    # Paso 1: SoftReset
    despertar_gps_soft_reset()
    time.sleep(1)
    
    # Paso 2: Solicitar NAV-PVT
    despertar_gps_nav_pvt()
    time.sleep(1)
    
    # Paso 3: Buscar NMEA
    encontradas = buscar_datos_validos()
    
    # Resumen
    print("\n" + "="*60)
    print("RESULTADO")
    print("="*60)
    
    if encontradas:
        print("\n✓✓✓ ¡GPS DESPERTADO Y FUNCIONANDO!")
        print("\nLa razón por la que no funciona main_fixed.py:")
        print("  • main_fixed.py usa protocolo UBX @ 38400 bps")
        print("  • Tu GPS envía NMEA @ 9600 bps")
        print("\nSOLUCIÓN:")
        print("  1. Usa main.py (original) que espera NMEA @ 9600")
        print("  2. O configura el GPS a UBX @ 38400 bps")
        print("\nRECOMENDADO: Usa main.py - es más simple\n")
    else:
        print("\n⚠️  GPS sigue en estado inválido")
        print("\nIntenta:")
        print("  1. Lleva el GPS afuera (necesita satélites)")
        print("  2. Espera 60 segundos (cold start)")
        print("  3. Recarga el firmware del GPS\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
