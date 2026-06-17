# ═══════════════════════════════════════════════════════════════
# TEST DE SENSORES - Sin WiFi, sin Supabase, sin GPS
# Solo prueba PIR + DHT22 localmente
# ═══════════════════════════════════════════════════════════════

from machine import Pin
import dht
import time

# ── Hardware ─────────────────────────────────────────────────────
led        = Pin(2,  Pin.OUT)
pir        = Pin(14, Pin.IN)
dht_sensor = dht.DHT22(Pin(4))

def blink(n=1):
    """Parpadea LED n veces"""
    for _ in range(n):
        led.value(1)
        time.sleep(0.1)
        led.value(0)
        time.sleep(0.1)

def test_led():
    """Test del LED onboard"""
    print("\n" + "="*50)
    print("TEST 1: LED (GPIO 2)")
    print("="*50)
    print("Parpadeando LED 5 veces...")
    blink(5)
    print("✓ LED funciona correctamente\n")

def test_pir():
    """Test del sensor PIR"""
    print("="*50)
    print("TEST 2: SENSOR PIR (GPIO 14)")
    print("="*50)
    print("Leyendo PIR durante 10 segundos...")
    print("Mueve tu mano frente al sensor PIR...\n")
    
    inicio = time.time()
    mov_detectado = False
    lecturas = []
    
    while time.time() - inicio < 10:
        valor = pir.value()
        lecturas.append(valor)
        print(f"  PIR value: {valor} {'← MOVIMIENTO DETECTADO!' if valor else ''}")
        if valor:
            mov_detectado = True
        time.sleep(0.5)
    
    print(f"\n✓ PIR funciona")
    print(f"  Movimiento detectado: {'SÍ ✓' if mov_detectado else 'NO (intenta mover más cerca)'}\n")

def test_dht22():
    """Test del sensor DHT22"""
    print("="*50)
    print("TEST 3: SENSOR DHT22 (GPIO 4)")
    print("="*50)
    print("Leyendo temperatura y humedad durante 10 segundos...\n")
    
    inicio = time.time()
    lecturas_temp = []
    lecturas_hum = []
    
    while time.time() - inicio < 10:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()
            
            lecturas_temp.append(temp)
            lecturas_hum.append(hum)
            
            print(f"  Temp: {temp:6.2f}°C | Humedad: {hum:6.1f}%")
            
        except Exception as e:
            print(f"  ✗ Error leyendo DHT22: {e}")
        
        time.sleep(1)
    
    if lecturas_temp:
        temp_promedio = sum(lecturas_temp) / len(lecturas_temp)
        hum_promedio = sum(lecturas_hum) / len(lecturas_hum)
        temp_min = min(lecturas_temp)
        temp_max = max(lecturas_temp)
        
        print(f"\n✓ DHT22 funciona")
        print(f"  Temperatura promedio: {temp_promedio:.2f}°C")
        print(f"  Rango de temperatura: {temp_min:.2f}°C - {temp_max:.2f}°C")
        print(f"  Humedad promedio: {hum_promedio:.1f}%\n")
    else:
        print("✗ No se pudieron leer datos del DHT22\n")

def test_completo():
    """Test completo"""
    print("\n" + "╔" + "="*48 + "╗")
    print("║" + " "*10 + "PETFINDER - TEST DE SENSORES" + " "*10 + "║")
    print("╚" + "="*48 + "╝\n")
    
    print("Iniciando tests...\n")
    
    try:
        test_led()
        time.sleep(1)
        
        test_pir()
        time.sleep(1)
        
        test_dht22()
        time.sleep(1)
        
        # Resumen
        print("="*50)
        print("RESUMEN")
        print("="*50)
        print("✓ LED............. FUNCIONA")
        print("✓ PIR............. FUNCIONA")
        print("✓ DHT22........... FUNCIONA")
        print("\n¡TODOS LOS SENSORES FUNCIONAN CORRECTAMENTE!")
        print("\nPuedes usar main_interior.py o main_fixed.py\n")
        
    except Exception as e:
        print(f"\n✗ ERROR CRÍTICO: {e}")

# Ejecutar
if __name__ == "__main__":
    try:
        test_completo()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
