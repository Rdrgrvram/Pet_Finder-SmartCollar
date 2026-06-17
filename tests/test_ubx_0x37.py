# ═══════════════════════════════════════════════════════════════
# ANALIZAR MENSAJE 0x01 0x37 (NAV-VELECEF)
# ═══════════════════════════════════════════════════════════════

from machine import UART
import time

print("\n" + "="*60)
print("ANALIZANDO MENSAJE 0x01 0x37")
print("="*60)

gps = UART(2, 115200)

# Limpiar buffer
while gps.any():
    gps.read()
    time.sleep(0.05)

print("\nLeyendo datos...")
buf = b""
for i in range(30):
    if gps.any():
        data = gps.read()
        if data:
            buf += data
    time.sleep(0.1)

print(f"Total recibido: {len(buf)} bytes\n")

# Buscar primer 0x01 0x37
i = 0
encontrado = False
while i < len(buf) - 6:
    if buf[i] == 0xB5 and buf[i+1] == 0x62:
        cls = buf[i+2]
        mid = buf[i+3]
        lng = buf[i+4] | (buf[i+5] << 8)
        
        if cls == 0x01 and mid == 0x37:
            if i + 6 + lng <= len(buf):
                print(f"[✓] Encontrado 0x01 0x37 @ offset {i}, {lng} bytes\n")
                
                payload = buf[i+6 : i+6+lng]
                
                # Mostrar payload hex
                print("Payload (hex):")
                for j in range(0, len(payload), 16):
                    hex_str = " ".join(f"{b:02X}" for b in payload[j:j+16])
                    print(f"    [{j:2d}] {hex_str}")
                
                print(f"\nPayload ({len(payload)} bytes total)")
                
                # Interpretar como valores int32 little-endian
                print("\nInterpretando como int32 LE (dividiendo entre 1e7):")
                for j in range(0, min(len(payload), 28), 4):
                    if j+4 <= len(payload):
                        val_raw = int.from_bytes(payload[j:j+4], 'little', True)
                        val_scaled = val_raw / 1e7
                        print(f"    [bytes {j:2d}-{j+3:2d}] {val_raw:12d} -> {val_scaled:12.6f}")
                
                encontrado = True
                break
        
        i += lng + 8
    else:
        i += 1

if not encontrado:
    print("❌ No se encontró mensaje 0x01 0x37")

print("\n" + "="*60)
