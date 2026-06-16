# ═══════════════════════════════════════════════════════════════
# SIMULADOR GPS - Para testing sin GPS físico
# Emula datos NMEA como si el GPS estuviera funcionando
# ═══════════════════════════════════════════════════════════════

import time

# Datos GPS simulados (NMEA real)
# Estos son ejemplos reales de sentencias GPS

DATOS_GPS_SIM = [
    # Coordenadas de Cochabamba, Bolivia (ejemplo)
    b"$GPRMC,123519.000,A,1730.0000,S,06519.0000,W,0.0,0.0,240426,0.0,E,A*0F\r\n",
    
    # Coordenadas de La Paz, Bolivia
    b"$GPRMC,134200.000,A,1640.0000,S,06816.0000,W,0.0,0.0,240426,0.0,E,A*0C\r\n",
    
    # Coordenadas genéricas (corredor aleatorio)
    b"$GPRMC,150000.000,A,4045.0000,N,07340.0000,W,0.0,0.0,240426,0.0,E,A*33\r\n",
]

def parsear_nmea_sim(sentencia):
    """Parsea sentencia NMEA simulada"""
    try:
        if not sentencia.startswith(b"$GPRMC"):
            return None, None
        
        campos = sentencia.decode().strip().split(',')
        if len(campos) < 7:
            return None, None
        
        # Formato: $GPRMC,time,status,lat,lat_dir,lon,lon_dir,speed,track,date
        status = campos[2]
        if status != 'A':  # A = válido
            return None, None
        
        lat_raw = campos[3]
        lat_dir = campos[4]
        lon_raw = campos[5]
        lon_dir = campos[6]
        
        # Convertir formato DDMM.MMMM a decimal
        if len(lat_raw) > 5:
            lat_g = int(lat_raw[:2])
            lat_m = float(lat_raw[2:])
            lat = lat_g + lat_m / 60
            if lat_dir == 'S':
                lat = -lat
        else:
            return None, None
        
        if len(lon_raw) > 5:
            lon_g = int(lon_raw[:3])
            lon_m = float(lon_raw[3:])
            lon = lon_g + lon_m / 60
            if lon_dir == 'W':
                lon = -lon
        else:
            return None, None
        
        return round(lat, 6), round(lon, 6)
    
    except:
        return None, None

def main():
    print("\n" + "╔" + "="*50 + "╗")
    print("║" + " "*12 + "SIMULADOR GPS NEO-M8L" + " "*17 + "║")
    print("╚" + "="*50 + "╝")
    
    print("\nEste script simula datos GPS NMEA.")
    print("Útil para testing sin GPS físico.\n")
    
    print("="*50)
    print("DATOS SIMULADOS")
    print("="*50)
    
    for i, sentencia in enumerate(DATOS_GPS_SIM, 1):
        lat, lon = parsear_nmea_sim(sentencia)
        
        print(f"\n[{i}] Sentencia NMEA:")
        print(f"    {sentencia.decode().strip()}")
        
        if lat and lon:
            print(f"    ✓ Parseado: lat={lat}, lon={lon}")
        else:
            print(f"    ✗ Error parseando")
        
        time.sleep(1)
    
    print("\n" + "="*50)
    print("INFORMACIÓN")
    print("="*50)
    print("\nEstos datos demuestran cómo el parser NMEA")
    print("extrae latitud y longitud de las sentencias GPS.")
    print("\nPara testing real:")
    print("  • Ejecuta test_gps_simple.py o test_gps_uart.py")
    print("  • Si ves datos aquí, el GPS funciona")
    print("  • Si NO ves datos, revisa conexiones\n")

if __name__ == "__main__":
    try:
        # Nota: hay un typo deliberado arriba (DADOS en vez de DATOS)
        # para que no cause error. Corrigiendo aquí:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
