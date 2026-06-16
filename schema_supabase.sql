-- ════════════════════════════════════════════════════════════════
--  PetFinder — Esquema de Base de Datos en Supabase (PostgreSQL)
--  Pregunta 3: Diseño de la Base de Datos
-- ════════════════════════════════════════════════════════════════

-- ── 1. TABLA PRINCIPAL: lecturas_collar ─────────────────────────
-- Ya existe en Supabase. Añadir las columnas faltantes:

ALTER TABLE lecturas_collar
  ADD COLUMN IF NOT EXISTS altitud   float8,   -- altitud en metros (del GPS)
  ADD COLUMN IF NOT EXISTS velocidad float8,   -- velocidad en km/h (del GPS)
  ADD COLUMN IF NOT EXISTS satelites int4;     -- cantidad de satélites visibles

-- Índice para consultas ordenadas por fecha (mejora rendimiento)
CREATE INDEX IF NOT EXISTS idx_lecturas_created_at
  ON lecturas_collar (created_at DESC);

-- ── 2. TABLA DE COMANDOS: comandos ──────────────────────────────
-- Permite enviar órdenes desde el dashboard al ESP32
-- El ESP32 consulta esta tabla y ejecuta la acción pendiente

CREATE TABLE IF NOT EXISTS comandos (
  id          bigserial    PRIMARY KEY,
  created_at  timestamptz  DEFAULT now() NOT NULL,
  accion      text         NOT NULL,        -- 'buzzer_on', 'buzzer_off'
  ejecutado   boolean      DEFAULT false,   -- false = pendiente, true = ya procesado
  ejecutado_en timestamptz                  -- cuándo lo procesó el ESP32
);

-- Índice para consultas de comandos pendientes
CREATE INDEX IF NOT EXISTS idx_comandos_pendientes
  ON comandos (ejecutado, created_at DESC)
  WHERE ejecutado = false;

-- ── 3. POLÍTICAS DE SEGURIDAD (Row Level Security) ───────────────
-- Habilitar RLS para proteger los datos

ALTER TABLE lecturas_collar ENABLE ROW LEVEL SECURITY;
ALTER TABLE comandos        ENABLE ROW LEVEL SECURITY;

-- Solo usuarios autenticados pueden leer lecturas
CREATE POLICY "Leer lecturas autenticado"
  ON lecturas_collar FOR SELECT
  USING (auth.role() = 'authenticated');

-- El ESP32 usa la anon key para insertar lecturas
CREATE POLICY "Insertar lectura anon"
  ON lecturas_collar FOR INSERT
  WITH CHECK (true);

-- Solo usuarios autenticados pueden insertar comandos (desde el dashboard)
CREATE POLICY "Insertar comando autenticado"
  ON comandos FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');

-- El ESP32 puede leer y actualizar comandos con anon key
CREATE POLICY "Leer comandos anon"
  ON comandos FOR SELECT
  USING (true);

CREATE POLICY "Actualizar comando anon"
  ON comandos FOR UPDATE
  USING (true);

-- ════════════════════════════════════════════════════════════════
--  ESTRUCTURA FINAL DE LAS TABLAS
-- ════════════════════════════════════════════════════════════════

-- lecturas_collar
-- ┌─────────────┬─────────────┬──────────────────────────────────┐
-- │ Campo       │ Tipo        │ Descripción                      │
-- ├─────────────┼─────────────┼──────────────────────────────────┤
-- │ id          │ bigserial   │ Clave primaria auto-incremental  │
-- │ created_at  │ timestamptz │ Fecha/hora automática Supabase   │
-- │ temperatura │ float8      │ Opcional (null sin sensor)       │
-- │ movimiento  │ boolean     │ Detección PIR (true/false)       │
-- │ latitud     │ float8      │ Coordenada GPS decimal           │
-- │ longitud    │ float8      │ Coordenada GPS decimal           │
-- │ altitud     │ float8      │ Altitud GPS en metros (NUEVO)    │
-- │ velocidad   │ float8      │ Velocidad GPS en km/h (NUEVO)    │
-- │ satelites   │ int4        │ Satélites visibles GPS (NUEVO)   │
-- └─────────────┴─────────────┴──────────────────────────────────┘

-- comandos
-- ┌──────────────┬─────────────┬─────────────────────────────────┐
-- │ Campo        │ Tipo        │ Descripción                     │
-- ├──────────────┼─────────────┼─────────────────────────────────┤
-- │ id           │ bigserial   │ Clave primaria auto-incremental │
-- │ created_at   │ timestamptz │ Cuándo se envió el comando      │
-- │ accion       │ text        │ 'buzzer_on' / 'buzzer_off'      │
-- │ ejecutado    │ boolean     │ false=pendiente, true=procesado │
-- │ ejecutado_en │ timestamptz │ Cuándo lo procesó el ESP32      │
-- └──────────────┴─────────────┴─────────────────────────────────┘
