# Informe Final — Sistema IoT: Collar Inteligente para Mascotas (PetFinder)

**Asignatura:** Sistemas Embebidos / Desarrollo IoT  
**Integrante(s):** ________________________  
**Fecha de entrega:** ________________________  
**Institución:** ________________________

---

## 1. Introducción

En los últimos años, la Internet de las Cosas (IoT) ha transformado de manera profunda la manera en que interactuamos con el entorno físico. Una de las aplicaciones más relevantes para la vida cotidiana es el monitoreo remoto de animales de compañía, cuya pérdida representa una experiencia angustiante para millones de familias en todo el mundo.

El presente proyecto propone el diseño e implementación de un sistema IoT denominado **PetFinder Smart Collar**, un collar inteligente para mascotas basado en el microcontrolador ESP32-C3. El prototipo físico final se implementó utilizando un **protoboard (breadboard)** para simplificar la distribución de energía y se integra por dos sensores físicos principales: movimiento por infrarrojos pasivos (PIR) y posicionamiento global (GPS NEO-M8L), conectados con una plataforma en la nube (Supabase) y un panel de control web accesible en tiempo real por cualquier usuario autenticado. 

*Nota de adaptación:* Aunque inicialmente se planificó la inclusión de un sensor de temperatura DHT22, debido a la falta de disponibilidad de dicho componente, el firmware embebido en MicroPython y los dashboards de visualización se adaptaron dinámicamente para operar de manera robusta sin él, dejando el campo de temperatura libre/null en la base de datos sin afectar la visualización de datos de posición y movimiento.

---

## 2. Objetivos

### 2.1 Objetivo General

Desarrollar un sistema IoT funcional que permita monitorear en tiempo real la actividad y la ubicación de una mascota mediante un collar inteligente basado en ESP32-C3, con almacenamiento en la nube y visualización mediante un dashboard web adaptado.

### 2.2 Objetivos Específicos

- Integrar sensores físicos (PIR para movimiento y GPS NEO-M8L para ubicación) en un sistema embebido con MicroPython usando conexiones en protoboard.
- Establecer una conexión WiFi estable desde el ESP32-C3 para transmitir datos hacia la API REST de Supabase.
- Diseñar y configurar una base de datos relacional en Supabase con los tipos de datos correctos, permitiendo campos opcionales para la temperatura.
- Implementar autenticación de usuarios mediante el servicio Auth de Supabase (JWT).
- Desarrollar un panel de control web responsivo y premium en HTML/JS vanilla y un dashboard alternativo en Streamlit que muestre los datos de actividad y coordenadas del mapa en tiempo real, adaptando la interfaz gráfica a la ausencia del sensor de temperatura.

---

## 3. Descripción del Sistema

El sistema PetFinder Smart Collar opera de la siguiente manera: el collar colocado en la mascota lee periódicamente (cada 10 segundos) el estado de movimiento a través del sensor PIR y la posición geográfica utilizando el módulo GPS NEO-M8L. Todos estos datos son empaquetados en formato JSON (enviando el valor de temperatura como `None/null`) y transmitidos mediante una solicitud HTTP POST a la API REST de Supabase, donde quedan almacenados de forma persistente.

El dueño de la mascota puede acceder al dashboard web (o al dashboard de Streamlit) desde cualquier dispositivo con navegador. Tras autenticarse con su correo electrónico y contraseña, visualiza el estado actual del collar: indicador dinámico y animado de movimiento, historial de actividad (gráfico de barras), y las coordenadas GPS renderizadas en un mapa interactivo de Leaflet/OpenStreetMap con un enlace directo a Google Maps para localizar a la mascota. Además, puede disparar remotamente un buzzer en el collar para ubicar al animal en casa.

---

## 4. Arquitectura del Sistema

```
┌────────────────────────────────────────────────────────────────┐
│                    COLLAR ESP32-C3 (Hardware)                  │
│                                                                │
│   PIR (GPIO3)  ──┐                                            │
│   GPS (UART1)  ──┼──► MicroPython main.py                    │
│   Buzzer(GPIO7) ─┘    │                                       │
│                       │ JSON + urequests                      │
│                       ▼                                       │
│              WiFi (802.11 b/g/n)                              │
└───────────────────────┬────────────────────────────────────────┘
                        │ HTTPS / REST API
                        ▼
┌────────────────────────────────────────────────────────────────┐
│                    SUPABASE (Backend)                          │
│                                                                │
│   PostgreSQL ──► tabla: lecturas_collar                        │
│   REST API  ──► POST /rest/v1/lecturas_collar                  │
│   Auth      ──► /auth/v1/token (JWT)                           │
└───────────────────────┬────────────────────────────────────────┘
                        │ fetch() / HTTPS
                        ▼
┌────────────────────────────────────────────────────────────────┐
│                    DASHBOARD WEB (Frontend)                    │
│                                                                │
│   HTML + CSS + JavaScript Vanilla / Streamlit (Python)         │
│   Leaflet Map ── mapa de trayectoria y posición actual         │
│   Chart.js / Plotly ── gráfico de actividad de movimiento      │
│   Auth UI  ── login / registro                                 │
│   Sincronización automatizada en vivo                          │
└────────────────────────────────────────────────────────────────┘
```

### 4.1 Flujo de datos detallado

1. El ESP32-C3 arranca, lee la configuración y se conecta a la red WiFi configurada.
2. Cada 10 segundos se ejecuta el ciclo de lectura: PIR (lectura continua por 2s) → GPS (lectura por UART con timeout).
3. Los datos de movimiento y coordenadas se empaquetan en un objeto JSON, asignando `null` al campo de temperatura.
4. Se realiza una petición HTTP POST al endpoint `/rest/v1/lecturas_collar` de Supabase con las cabeceras de autenticación.
5. Supabase almacena el registro en PostgreSQL y asigna el timestamp automático.
6. El dashboard web (o de Streamlit) realiza peticiones GET para obtener las lecturas en orden descendente y actualiza las métricas y el mapa dinámicamente.

---

## 5. Diseño del Circuito (Protoboard)

### 5.1 Tabla de conexiones de pines

| Componente    | Pin del componente | GPIO ESP32-C3 | Conexión en Protoboard / Notas |
|---------------|-------------------|---------------|-------------------------------|
| **GPS NEO-M8L** | VCC               | 3V3           | Bus de alimentación positivo de 3.3V (Línea Roja "+") |
| | GND               | GND           | Bus de alimentación negativo (Línea Azul/Negra "-") |
| | TX                | GPIO4 (RX1)   | UART1: Recepción de sentencias NMEA |
| | RX                | GPIO5 (TX1)   | UART1: Transmisión de comandos (cruzado) |
| **Sensor PIR** | VCC               | 5V / VIN      | Conectado al pin 5V (USB) del ESP32-C3 |
| | GND               | GND           | Bus de alimentación negativo (Línea Azul/Negra "-") |
| | OUT               | GPIO3         | Entrada digital: HIGH (movimiento) / LOW (reposo) |
| **Buzzer Activo**| (+)               | GPIO7         | Salida digital: HIGH activa sonido |
| | (-)               | GND           | Bus de alimentación negativo (Línea Azul/Negra "-") |
| **LED onboard** | (+)               | GPIO8         | Indicador de estado en serie con resistencia de 220Ω |
| | (-)               | GND           | Bus de alimentación negativo (Línea Azul/Negra "-") |

### 5.2 Descripción de cada sensor

**PIR (Passive Infrared Sensor):** Detecta la radiación infrarroja de cuerpos en movimiento dentro de su rango. Emite una señal digital HIGH al pin GPIO3 del ESP32-C3 cuando hay presencia activa. Se calibra mediante los potenciómetros del sensor físico.

**GPS NEO-M8L (u-blox):** Receptor GNSS de alta sensibilidad que se comunica mediante UART a 115200 baudios. Proporciona tramas NMEA ($GPRMC) con las coordenadas de la mascota para geolocalización.

**Buzzer Activo:** Generador de sonido piezoeléctrico de 5V controlado desde el pin GPIO7. Permite emitir una alerta sonora a distancia desde la web para encontrar a la mascota.

---

## 6. Configuración de Supabase

Se configuró un proyecto en la nube en Supabase, diseñando dos tablas con Row Level Security (RLS) activo para protección de datos:

1. **`lecturas_collar`**: Almacena las lecturas históricas (temperatura, movimiento, latitud, longitud, altitud, velocidad, satélites, timestamp).
2. **`comandos`**: Registra los comandos remotos enviados por el usuario (ej: `buzzer_on`) para ser leídos y ejecutados por el firmware del ESP32-C3.

---

## 7. Tecnologías Utilizadas

| Componente | Tecnología | Justificación |
|---|---|---|
| Microcontrolador | ESP32-C3 | WiFi integrado, arquitectura RISC-V de bajo consumo y bajo coste. |
| Firmware | MicroPython 1.22 | Desarrollo ágil en Python embebido, uso de `urequests` y `ujson`. |
| Base de datos / BaaS | Supabase (PostgreSQL) | Backend en la nube automático, REST API nativa y autenticación JWT. |
| Web Dashboard | HTML5 / CSS / Vanilla JS | Sin frameworks pesados; utiliza Tailwind CSS para una interfaz premium. |
| Python Dashboard | Streamlit / Plotly | Interfaz analítica rápida con mapas interactivos y control remoto integrado. |

---

## 8. Resultados y Conclusión

El collar inteligente **PetFinder** funciona de manera óptima sobre un protoboard robusto. La ausencia del sensor de temperatura DHT22 no interfirió con el correcto envío de coordenadas de geolocalización y eventos de movimiento en tiempo real a la nube. Ambos dashboards (HTML y Streamlit) se adaptaron estéticamente para mantener una interfaz limpia de tres columnas, centrando la atención en el rastreo en vivo y la seguridad de la mascota. El sistema de control remoto de sonido (buzzer) responde con una latencia de apenas unos segundos tras presionar el botón web, logrando un prototipo IoT robusto, funcional y listo para pruebas de campo.
