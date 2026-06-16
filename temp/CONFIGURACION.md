# 🐕 PetFinder Smart Collar - Configuración Completa

## 📋 Tabla de Contenidos
1. [Componentes](#componentes)
2. [Esquema de Conexiones](#esquema-de-conexiones)
3. [Configuración GPIO](#configuración-gpio)
4. [Supabase](#supabase)
5. [Instalación y Setup](#instalación-y-setup)
6. [Ejecución](#ejecución)
7. [Dashboard](#dashboard)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Componentes

### Hardware Principal
| Componente | Modelo | Voltaje | Cantidad |
|-----------|--------|---------|----------|
| Microcontrolador | ESP32 DevKit V1 | 3.3V | 1 |
| GPS | NEO-6M | 3.3V | 1 |
| Sensor PIR | HC-SR501 | 5V → 3.3V | 1 |
| Sensor Temperatura | DHT22 | 3.3V | 1 |
| Resistencia | 10kΩ | - | 1 |
| Batería | LiPo 3.7V | 3.7V | 1 |
| Regulador | AMS1117 3.3V | - | 1 (si usas batería) |

### Software
- **MicroPython** (firmware ESP32)
- **Thonny IDE** (programación)
- **Python 3.x** (scripts PC)
- **u-center** (opcional, configurar GPS)

---

## 📡 Esquema de Conexiones

### ESP32 DevKit V1 (30 pines)

```
┌─────────────────────────────────────┐
│         ESP32 DevKit V1             │
│                                     │
│  3V3 ───────┬─── PIR VCC            │
│             │                       │
│  GND ───────┼─── PIR GND            │
│             ├─── DHT GND            │
│             ├─── GPS GND            │
│             │                       │
│  GPIO 4 ────┼─── DHT data           │
│  GPIO 14 ───┼─── PIR out            │
│  GPIO 16 ───┼─── GPS TX             │
│  GPIO 17 ───┼─── GPS RX             │
│             │                       │
│  5V ────────┼─── (solo si USB)      │
└─────────────────────────────────────┘
```

### Conexiones Detalladas

#### **ESP32 ↔ PIR Motion Sensor (HC-SR501)**
```
ESP32 3V3  → PIR VCC
ESP32 GND  → PIR GND
ESP32 GPIO14 → PIR OUT
```

#### **ESP32 ↔ DHT22 Temperature**
```
ESP32 3V3  → DHT VCC
ESP32 GND  → DHT GND
ESP32 GPIO 4 → DHT DATA (con resistencia 10kΩ a VCC)
```

#### **ESP32 ↔ NEO-6M GPS**
```
ESP32 3V3  → GPS VCC
ESP32 GND  → GPS GND
ESP32 GPIO 16 (UART2 RX) → GPS TX
ESP32 GPIO 17 (UART2 TX) → GPS RX
```

---

## 🎯 Configuración GPIO

| GPIO | Función | Tipo | Voltaje |
|------|---------|------|---------|

| 4 | DHT22 Data | Input/Output | 3.3V |
| 14 | PIR Motion | Input | 3.3V |
| 16 | GPS TX | UART2 RX | 3.3V |
| 17 | GPS RX | UART2 TX | 3.3V |

### UART Configuración
```
UART2 (ESP32 estándar):
- Baudrate: 9600 bps (NEO-6M)
- Data bits: 8
- Stop bits: 1
- Parity: None
- TX: GPIO 17
- RX: GPIO 16
```

---

## ☁️ Supabase

### Crear Proyecto
1. Ir a https://supabase.com
2. Crear cuenta / Login
3. Nuevo proyecto → Region: América del Sur

### Tabla `lecturas_collar`
```sql
CREATE TABLE lecturas_collar (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP DEFAULT NOW(),
  temperatura FLOAT,
  movimiento BOOLEAN,
  latitud FLOAT,
  longitud FLOAT
);
```

### API Keys
Encontrar en: `Settings → API → Project API keys`
- **anon key**: Usar en `SUPABASE_ANON_KEY`
- **service_role**: NO usar en ESP32

### Credenciales en Código
```python
SUPABASE_URL = "https://[PROJECT_ID].supabase.co"
SUPABASE_ANON_KEY = "[ANON_KEY]"
```

---

## 🚀 Instalación y Setup

### Paso 1: Instalar MicroPython en ESP32

#### Con esptool.py
```bash
# Instalar esptool
pip install esptool

# Descargar firmware MicroPython desde:
# https://micropython.org/download/esp32/

# Grabar firmware
esptool.py --chip esp32 --port COM3 erase_flash
esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-20231216-v1.22.0.bin
```

#### Con Thonny (más fácil)
1. Instalar Thonny: https://thonny.org/
2. Conectar ESP32 por USB
3. En Thonny → `Tools → Options → Interpreter`
4. Seleccionar "MicroPython (ESP32)"
5. Seleccionar puerto COM
6. Click "Install or update MicroPython"

### Paso 2: Instalar Librerías MicroPython

En Thonny, ejecutar en terminal:
```python
import upip
upip.install('micropython-dht')
upip.install('micropython-requests')
```

### Paso 3: Copiar Código Principal

1. En Thonny, abrir `main_neo6m.py`
2. Cambiar credenciales WiFi y Supabase
3. Conectar ESP32 por USB
4. Click "Run" o F5

---

## ▶️ Ejecución

### Opción A: NEO-6M Real (Recomendado)
```bash
# En Thonny
main_neo6m.py  # F5
```

**Esperado:**
```
[WiFi] Conectado: 192.168.X.X
[PIR] Movimiento: 0
[DHT] 25.5°C
[GPS] ✓ NMEA válido: lat=-17.389, lon=-66.156
[HTTP] ✓ Status: 201
[HTTP] ✓ Datos guardados
```

### Opción B: GPS Simulado (Testing indoors)
```bash
# En Thonny
main_gps_simulado.py  # F5
```

Genera coordenadas ficticias para testing sin GPS.

### Opción C: Sin GPS (Solo sensores)
```bash
# En Thonny
main_interior.py  # F5
```

Solo PIR y DHT22, sin posición.

---

## 📊 Dashboard

### Abrir Dashboard
```bash
# Abrir en navegador
file:///C:/Users/Lenovo/Downloads/PetFinder_Beta/dashboard.html
```

### Características
- 🗺️ Mapa interactivo (última posición)
- 📈 Gráfico temperatura en tiempo real
- 🚨 Indicador movimiento
- ⏰ Timestamp última lectura
- 🔄 Auto-actualiza cada 5 segundos

### Conexión a Supabase
El dashboard se conecta automáticamente si tienes las credenciales correctas en el código.

---

## 🛠️ Troubleshooting

### ❌ WiFi no conecta
**Síntomas:** `[WiFi] Esperando... (1/15)`

**Soluciones:**
1. Verificar SSID y contraseña en código
2. Router debe tener banda 2.4GHz (ESP32 no soporta 5GHz)
3. Verificar que ESP32 tenga buena señal
4. Reintentar con `machine.reset()`

### ❌ GPS sin señal
**Síntomas:** `[GPS] Timeout sin fix`

**Soluciones:**
1. Llevar ESP32 a lugar abierto (techo, terraza)
2. Esperar 30-60 segundos para primer fix (cold start)
3. Verificar conexiones GPIO 16/17
4. Probar con `test_gps_diagnostico.py`

### ❌ Supabase error ETIMEDOUT
**Síntomas:** `[HTTP] ✗ Error: [Errno 116] ETIMEDOUT`

**Soluciones:**
1. Verificar WiFi conectado
2. Verificar URLs y API key correctas
3. Usar `test_diagnostico_conexion.py` para debugging
4. Revisar firewall router

### ❌ DHT22 Error
**Síntomas:** `[DHT] Error`

**Soluciones:**
1. Verificar conexión GPIO 4
2. Agregar resistencia 10kΩ entre GPIO4 y 3V3
3. Instalar librería: `upip.install('micropython-dht')`
4. Probar con `test_sensores.py`

### ❌ PIR no detecta
**Síntomas:** `[PIR] Movimiento: 0` siempre

**Soluciones:**
1. Verificar conexión GPIO 14
2. HC-SR501 necesita 30-60 segundos de estabilización
3. Ajustar potenciómetro sensibilidad
4. Probar con `test_sensores.py`

---

## 📁 Estructura de Archivos

```
PetFinder_Beta/
├── main_neo6m.py              ✅ Principal (NEO-6M real)
├── main_gps_simulado.py       🟡 Con GPS simulado
├── main_interior.py           🟡 Sin GPS
├── dashboard.html             🗺️ Frontend web
├── test_sensores.py           🧪 Validar PIR/DHT
├── test_diagnostico_conexion.py 🧪 Validar WiFi/Supabase
├── CONFIGURACION.md           📖 Este archivo
└── ...otros scripts...
```

---

## 📱 Uso en Producción

### Checklist
- [ ] WiFi conecta correctamente
- [ ] Sensores (PIR, DHT) funcionan
- [ ] GPS obtiene fix (outdoor)
- [ ] Datos llegan a Supabase
- [ ] Dashboard se actualiza
- [ ] Batería cargada

### Montaje Final
1. Colocar ESP32 + GPS en collar
2. Conectar batería LiPo
3. Configurar auto-ejecución (guardar main_neo6m.py como main.py)
4. Llevar a mascota afuera
5. Monitorear dashboard en tiempo real

---

## 🔗 Enlaces Útiles

- **Supabase:** https://supabase.com
- **MicroPython:** https://micropython.org
- **Thonny IDE:** https://thonny.org
- **u-center (GPS):** https://www.u-blox.com/en/product/u-center
- **NEO-6M Spec:** https://www.u-blox.com/sites/default/files/products/documents/NEO-6_DataSheet_(GPS.G6-HW-09005).pdf
- **ESP32 Pinout:** https://randomnerdtutorials.com/esp32-pinout-reference-gpios/

---

## ✅ Checklist Inicial

1. **Hardware:**
   - [ ] ESP32 conectado por USB
   - [ ] Todos los sensores conectados
   - [ ] GPS conectado (GPIO 16/17)
   - [ ] LED parpadea (test)

2. **Software:**
   - [ ] MicroPython instalado en ESP32
   - [ ] Thonny instalado en PC
   - [ ] Librerías MicroPython instaladas

3. **Cloud:**
   - [ ] Cuenta Supabase creada
   - [ ] Tabla `lecturas_collar` creada
   - [ ] API key copiada al código

4. **Pruebas:**
   - [ ] `test_sensores.py` → todos OK
   - [ ] `main_neo6m.py` → conecta WiFi
   - [ ] Datos en Supabase (revisar tabla)
   - [ ] Dashboard actualiza

---

## 🆘 Soporte Rápido

**Si algo no funciona:**

1. Ejecutar script de diagnóstico relevante
2. Copiar output completo
3. Revisar esta guía en sección Troubleshooting
4. Si persiste, revisar logs en Supabase y verificar endpoints API

**Logs útiles:**
```python
# Agregar al inicio de main_neo6m.py
import sys
sys.stdout = open('/dev/null', 'w')  # Sin esto, para ver logs
```

---

Última actualización: **28/04/2026**  
Versión: **1.0 - Producción**
