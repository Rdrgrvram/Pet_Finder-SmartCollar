# 🐾 PetFinder Smart Collar IoT

PetFinder es un sistema integral de Internet de las Cosas (IoT) diseñado para el monitoreo en tiempo real y la localización de mascotas. Utiliza un ESP32 como nodo sensor (Edge), Supabase como plataforma BaaS y una Progressive Web App (PWA) interactiva como interfaz de usuario.

## 📐 Arquitectura del Sistema
El sistema se compone de tres capas principales:
1. **Hardware/Firmware:** ESP32 DevKit V1 programado en MicroPython v1.28.0.
2. **Backend:** Supabase (PostgreSQL) con políticas de Row Level Security (RLS) y API REST nativa.
3. **Frontend:** PWA desarrollada con HTML5, JavaScript Vanilla, Tailwind CSS, Leaflet.js y Chart.js.

## 🛠️ Hardware y Pinout (ESP32 DevKit V1)
| Componente | Interfaz / Pin | Descripción |
| :--- | :--- | :--- |
| **NEO-M8L** | UART2 (TX=17, RX=16) | Módulo GPS de alta precisión a 9600 baudios. |
| **NTC 10kΩ** | GPIO 36 (VP) | Termistor para medición de temperatura (Divisor 10kΩ). |
| **SW-520D** | GPIO 18 | Sensor de vibración con resistencia pull-up física de 10k. |
| **Buzzer Activo**| GPIO 19 | Alerta sonora de 5V conmutada vía transistor NPN 2N2222A. |
| **LED Status** | GPIO 2 | LED integrado en placa para feedback visual de red. |

> **⚠️ Alerta de Hardware:** El buzzer opera a 5V (conectado al riel VIN). El GPIO 19 a 3.3V ataca la base de un transistor 2N2222A mediante una resistencia de 2kΩ para proporcionar aislamiento de voltaje y proteger el microcontrolador.

## 🚀 Guía de Despliegue

### 1. Base de Datos (Supabase)
1. Crea un nuevo proyecto en Supabase.
2. Ve al SQL Editor y ejecuta el script completo de `/db/schema_supabase.sql`.
3. Esto creará las tablas `lecturas_collar` y `comandos`, y configurará las políticas RLS.

### 2. Firmware (MicroPython)
1. Flashea el ESP32 DevKit V1 con el firmware de MicroPython.
2. Abre el archivo `/firmware/main.py`.
3. Edita las variables de configuración con tus datos:
   - `WIFI_SSID` y `WIFI_PASSWORD`
   - `SUPABASE_URL` y `SUPABASE_ANON_KEY`
4. Sube el script a la placa usando Thonny IDE.

### 3. Frontend (PWA)
1. Configura la URL y la API Key de Supabase en `/frontend/dashboard.html`.
2. Sirve los archivos estáticos (`dashboard.html`, `manifest.json`, `sw.js` e íconos) utilizando un servidor web (ej. Vercel, Netlify o GitHub Pages).
3. Accede desde cualquier dispositivo móvil e instala la PWA en la pantalla de inicio.

## 🔐 Seguridad Implementada
- **RLS (Row Level Security):** Inserciones limitadas al rol `anon` (Hardware), lecturas limitadas al rol `authenticated` (Usuarios).
- **JWT (JSON Web Tokens):** Autenticación de sesiones de usuario gestionada vía Supabase Auth.
- **HTTPS/TLS 1.3:** Encriptación obligatoria en tránsito para todas las comunicaciones REST.

## 👥 Autores
**Equipo: Ping-Ones**
- José Andrés Manzaneda Manzaneda
- Rodrigo Gabriel Rivera Mayan
- Mauricio Orlando Rivera Mayan
- Fernando José Catari Mamani

*Ingeniería de Sistemas, Universidad Católica Boliviana San Pablo (2026).*
