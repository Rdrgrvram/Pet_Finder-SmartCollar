# ═══════════════════════════════════════════════════════════════
# DIAGNÓSTICO GPS AFUERA - Analiza datos en tiempo real
# ═══════════════════════════════════════════════════════════════

from machine import UART
import time

def analizar_datos_gps():
    """Lee y analiza datos brutos del GPS"""
    print("\n" + "="*60)
    print("ANALIZANDO DATOS GPS EN VIVO")
    print("="*60)
    print("\nLeyendo durante 30 segundos...")
    print("(Verás exactamente qué envía el GPS)\n")
    
    gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
    
    inicio = time.time()
    datos_raw = b""
    nmea_count = 0
    ubx_count = 0
    basura_count = 0
    
    while time.time() - inicio < 30:
        if gps.any():
            data = gps.read(256)
            datos_raw += data
            
            # Analizar tipo de datos
            if b"$GN" in data or b"$GP" in data:
                nmea_count += 1
                # Mostrar sentencias NMEA
                lineas = data.split(b"\n")
                for linea in lineas:
                    if linea.startswith(b"$"):
                        print(f"  NMEA: {linea.decode('utf-8', errors='ignore').strip()[:80]}")
            
            elif data[0:2] == b'\xb5\x62':  # UBX header
                ubx_count += 1
                print(f"  UBX: {data[:20]}")
            else:
                basura_count += 1
        
        time.sleep(0.1)
    
    gps.deinit()
    
    # Análisis
    print("\n" + "="*60)
    print("ANÁLISIS")
    print("="*60)
    print(f"\nSentencias NMEA encontradas: {nmea_count}")
    print(f"Mensajes UBX encontrados: {ubx_count}")
    print(f"Datos basura/desconocidos: {basura_count}")
    
    if nmea_count > 0:
        print("\n✓ El GPS envía NMEA (correcto para main_nmea_9600.py)")
    elif ubx_count > 0:
        print("\n✓ El GPS envía UBX (usa main_fixed.py)")
    else:
        print("\n✗ El GPS NO está enviando datos válidos")
    
    return nmea_count, ubx_count, basura_count

def despertar_gps_completo():
    """Intenta despertar completamente el GPS"""
    print("\n" + "="*60)
    print("DESPERTANDO GPS COMPLETAMENTE")
    print("="*60)
    
    # Comando 1: Cold start (reinicio completo)
    print("\n[1] Enviando COLD START...")
    UBX_COLD_START = bytes([
        0xB5, 0x62, 0x06, 0x04, 0x04, 0x00,
        0x00, 0x00, 0x01, 0x00, 0x0F, 0x66
    ])
    
    try:
        gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
        gps.write(UBX_COLD_START)
        print("    ✓ Enviado")
        time.sleep(2)
        gps.deinit()
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # Comando 2: Habilitar mensajes NMEA
    print("\n[2] Habilitando salida NMEA...")
    UBX_ENABLE_NMEA = bytes([
        0xB5, 0x62, 0x06, 0x00, 0x14, 0x00,
        0x00, 0xFF, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x01, 0x00, 0x00, 0x1E, 0xCA
    ])
    
    try:
        gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
        gps.write(UBX_ENABLE_NMEA)
        print("    ✓ Enviado")
        time.sleep(2)
        gps.deinit()
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # Comando 3: Solicitar NAV-PVT
    print("\n[3] Solicitando posición (NAV-PVT)...")
    UBX_NAV_PVT = bytes([
        0xB5, 0x62, 0x01, 0x07, 0x00, 0x00, 0x08, 0x19
    ])
    
    try:
        gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
        gps.write(UBX_NAV_PVT)
        print("    ✓ Enviado")
        time.sleep(1)
        gps.deinit()
    except Exception as e:
        print(f"    ✗ Error: {e}")

def modo_escucha_pasivo():
    """Solo escucha sin enviar nada"""
    print("\n" + "="*60)
    print("MODO ESCUCHA PASIVO")
    print("="*60)
    print("\nEscuchando GPS durante 60 segundos...")
    print("(Sin enviar comandos)\n")
    
    gps = UART(2, baudrate=9600, tx=17, rx=16, rxbuf=512)
    
    inicio = time.time()
    linea_count = 0
    
    buf = b""
    while time.time() - inicio < 60:
        if gps.any():
            data = gps.read(256)
            buf += data
            
            while b"\n" in buf:
                linea, buf = buf.split(b"\n", 1)
                linea = linea.decode('utf-8', errors='ignore').strip()
                
                if linea.startswith("$"):
                    linea_count += 1
                    # Detectar si tiene fix (status 'A')
                    if "A" in linea:
                        print(f"  ✓ {linea[:80]}")
                    else:
                        print(f"  ✗ {linea[:80]}")
        
        time.sleep(0.1)
    
    gps.deinit()
    
    print(f"\nTotal de líneas NMEA: {linea_count}")
    return linea_count

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "DIAGNÓSTICO GPS - MODO TERRAZA/AFUERA" + " "*10 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\n⚠️  Si aún está en INDOOR, este test puede no funcionar")
    print("    (Necesita satélites reales)\n")
    
    # Test 1: Analizar datos
    nmea, ubx, basura = analizar_datos_gps()
    
    time.sleep(2)
    
    if nmea == 0 and ubx == 0:
        print("\n" + "="*60)
        print("SIN DATOS - Intentando despertar...")
        print("="*60)
        
        # Test 2: Despertar
        despertar_gps_completo()
        
        time.sleep(3)
        
        # Test 3: Escucha pasiva
        lineas = modo_escucha_pasivo()
        
        if lineas == 0:
            print("\n" + "="*60)
            print("DIAGNÓSTICO FINAL")
            print("="*60)
            print("\n✗ El GPS sigue sin responder")
            print("\nProbables causas:")
            print("  1. Still en INTERIOR (no hay satélites)")
            print("  2. GPS sin antena o antena defectuosa")
            print("  3. Firmware del GPS corrompido")
            print("  4. Conexión UART defectuosa")
            print("\nIntenta:")
            print("  • Acercarte más al cielo abierto")
            print("  • Desconectar/reconectar el GPS (power cycle)")
            print("  • Usar u-center para revisar el firmware")
    else:
        print("\n✓ GPS respondiendo correctamente")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
