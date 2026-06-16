# ═══════════════════════════════════════════════════════════════
# DEBUG UBX - Ver bytes exactos del GPS
# ═══════════════════════════════════════════════════════════════

from machine import UART, Pin
import time

print("\n" + "="*60)
print("DEBUG UBX - ANALIZANDO PAYLOAD")
print("="*60)

gps = UART(2, 115200)

# Limpiar buffer
print("\n[1] Limpiando buffer...")
while gps.any():
    gps.read()
    time.sleep(0.05)

# Mensaje de poll NAV-PVT
print("\n[2] Solicitando NAV-PVT...")
UBX_NAV_PVT_REQ = bytes([0xB5, 0x62, 0x01, 0x07, 0x00, 0x00, 0x08, 0x19])
gps.write(UBX_NAV_PVT_REQ)
time.sleep(1)

# Leer buffer
print("\n[3] Leyendo buffer (5 segundos)...\n")
buf = b""
for i in range(50):
    if gps.any():
        data = gps.read()
        if data:
            buf += data
            print(f"[{i}] Recibido {len(data)} bytes")
    time.sleep(0.1)

print(f"\nTotal: {len(buf)} bytes\n")

# Buscar header UBX
print("[4] Buscando headers UBX (0xB5 0x62)...\n")
i = 0
contador = 0
while i < len(buf) - 6:
    if buf[i] == 0xB5 and buf[i+1] == 0x62:
        cls = buf[i+2]
        mid = buf[i+3]
        lng = buf[i+4] | (buf[i+5] << 8)
        
        print(f"    [{contador}] @ offset {i}:")
        print(f"         Class: 0x{cls:02X}, ID: 0x{mid:02X}, Len: {lng}")
        
        # Si es NAV-PVT (0x01 0x07)
        if cls == 0x01 and mid == 0x07:
            if i + 6 + lng <= len(buf):
                payload = buf[i+6 : i+6+lng]
                print(f"         ✓ NAV-PVT encontrado, {len(payload)} bytes de payload\n")
                
                # Mostrar payload en hex
                print("         Payload (hex):")
                for j in range(0, len(payload), 16):
                    hex_str = " ".join(f"{b:02X}" for b in payload[j:j+16])
                    print(f"             [{j:2d}] {hex_str}")
                
                print()
                
                # Intentar extraer lat/lon de diferentes posiciones
                print("         Intentando extraer lat/lon:")
                
                # Según NEO-M8 spec: bytes 24-27 lon, 28-31 lat
                if len(payload) >= 32:
                    lon_raw = int.from_bytes(payload[24:28], 'little', True)
                    lat_raw = int.from_bytes(payload[28:32], 'little', True)
                    lat = lat_raw / 1e7
                    lon = lon_raw / 1e7
                    print(f"             [bytes 24-27, 28-31] lat={lat:.6f}, lon={lon:.6f}")
                
                # Intentar otras posiciones
                if len(payload) >= 36:
                    lon_raw2 = int.from_bytes(payload[20:24], 'little', True)
                    lat_raw2 = int.from_bytes(payload[24:28], 'little', True)
                    lat2 = lat_raw2 / 1e7
                    lon2 = lon_raw2 / 1e7
                    print(f"             [bytes 20-23, 24-27] lat={lat2:.6f}, lon={lon2:.6f}")
        
        contador += 1
        i += lng + 8  # Saltar este mensaje
    else:
        i += 1

print("\n" + "="*60)
