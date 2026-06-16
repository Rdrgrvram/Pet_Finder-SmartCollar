# ═══════════════════════════════════════════════════════════════
# CAMBIAR GPS A NMEA @ 9600 BPS
# Usar mensajes NMEA más simples y confiables
# ═══════════════════════════════════════════════════════════════

from machine import UART, Pin
import time

print("\n" + "="*60)
print("CONFIGURAR GPS A NMEA")
print("="*60)

gps = UART(2, 115200)

# Reset GPIO 12
print("\n[1] Reset GPIO 12...")
try:
    reset_pin = Pin(12, Pin.OUT)
    reset_pin.value(0)
    time.sleep(0.1)
    reset_pin.value(1)
    time.sleep(1)
    print("    ✓ Reset enviado")
except:
    print("    ℹ️  GPIO 12 no disponible")

# Enviar comando para cambiar a NMEA @ 9600 bps
print("\n[2] Enviando config UBX para cambiar a NMEA...")

# UBX-CFG-PRT: Configurar puerto UART a 9600 bps con protocolo NMEA
# Estructura: B5 62 06 00 14 00 [portID] [reserved] [txReady] [baudrate] [inProto] [outProto] [flags] [reserved2] [checksum]
CFG_PRT_NMEA = bytes([
    0xB5, 0x62,              # Header
    0x06, 0x00,              # CFG-PRT
    0x14, 0x00,              # Longitud (20 bytes)
    0x01,                    # Port ID = UART1
    0x00,                    # Reserved
    0x00, 0x00,              # TxReady
    0x80, 0x25, 0x00, 0x00,  # Baudrate = 9600 bps (0x2580 en little-endian)
    0x01,                    # inProto: NMEA
    0x01,                    # outProto: NMEA
    0x00, 0x00,              # Flags
    0x00, 0x00,              # Reserved
    0x1E, 0xE7               # Checksum (aproximado)
])

try:
    gps.write(CFG_PRT_NMEA)
    print("    ✓ Comando enviado")
    time.sleep(2)
except Exception as e:
    print(f"    Error: {e}")

# Cambiar a 9600 bps para verificar
print("\n[3] Cambiando a 9600 bps...")
gps.deinit()
time.sleep(0.5)
gps = UART(2, 9600)
print("    ✓ UART @ 9600 bps")

# Leer respuesta
print("\n[4] Leyendo respuesta (5 segundos)...\n")
for i in range(50):
    if gps.any():
        data = gps.read()
        if data:
            print(f"    [{i}] {data}")
            # Buscar $GN o $GP (NMEA válido)
            if b"$GN" in data or b"$GP" in data:
                print("\n    ✓✓✓ ¡NMEA ENCONTRADO!")
                break
    time.sleep(0.1)

print("\n" + "="*60)
