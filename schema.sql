-- ─────────────────────────────────────────────────────────────
-- MateShop — Inicializacion de la base de datos PostgreSQL
-- ─────────────────────────────────────────────────────────────
-- Ejecutar:  psql -U postgres -f schema.sql
-- ─────────────────────────────────────────────────────────────

-- Crear base de datos (ejecutar como superusuario si no existe)
-- CREATE DATABASE mateshop;
-- \c mateshop

-- ── EXTENSIONES ──────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── TABLA: productos ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(120)   NOT NULL,
    description TEXT,
    price       NUMERIC(10,2)  NOT NULL CHECK (price >= 0),
    stock       INTEGER        NOT NULL DEFAULT 0 CHECK (stock >= 0),
    tag         VARCHAR(50)    NOT NULL DEFAULT 'clasico',
    image_url   TEXT,
    created_at  TIMESTAMP      DEFAULT NOW(),
    updated_at  TIMESTAMP      DEFAULT NOW()
);

-- ── TABLA: usuarios ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(180)  UNIQUE NOT NULL,
    password_hash TEXT          NOT NULL,
    full_name     VARCHAR(120)  NOT NULL,
    role          VARCHAR(20)   NOT NULL DEFAULT 'customer'
                                CHECK (role IN ('customer', 'admin')),
    created_at    TIMESTAMP     DEFAULT NOW()
);

-- ── DATOS DE PRUEBA — PRODUCTOS ──────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id                           SERIAL PRIMARY KEY,
    invoice_number               VARCHAR(40) UNIQUE NOT NULL,
    user_id                      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total                        NUMERIC(10,2) NOT NULL CHECK (total >= 0),
    status                       VARCHAR(30) NOT NULL DEFAULT 'confirmado',
    payment_method               VARCHAR(30) NOT NULL DEFAULT 'tarjeta_simulada',
    shipping_name                VARCHAR(120) NOT NULL,
    shipping_phone               VARCHAR(40) NOT NULL,
    shipping_email               VARCHAR(180) NOT NULL,
    shipping_city                VARCHAR(120) NOT NULL,
    shipping_address             TEXT NOT NULL,
    shipping_postal_code         VARCHAR(20) NOT NULL,
    shipping_notes               TEXT,
    card_holder                  VARCHAR(120) NOT NULL,
    card_last4                   VARCHAR(4) NOT NULL,
    card_expiration              VARCHAR(10) NOT NULL,
    mercado_pago_preference_id   VARCHAR(120),
    mercado_pago_payment_id      VARCHAR(120),
    mercado_pago_status          VARCHAR(80),
    created_at                   TIMESTAMP DEFAULT NOW()
);

ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_method VARCHAR(30) NOT NULL DEFAULT 'tarjeta_simulada';
ALTER TABLE orders ADD COLUMN IF NOT EXISTS mercado_pago_preference_id VARCHAR(120);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS mercado_pago_payment_id VARCHAR(120);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS mercado_pago_status VARCHAR(80);

CREATE TABLE IF NOT EXISTS order_items (
    id           SERIAL PRIMARY KEY,
    order_id     INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id   INTEGER REFERENCES products(id) ON DELETE SET NULL,
    product_name VARCHAR(120) NOT NULL,
    unit_price   NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    quantity     INTEGER NOT NULL CHECK (quantity > 0),
    subtotal     NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0)
);

INSERT INTO products (name, description, price, stock, tag) VALUES
    ('Mate Calabaza Natural',     'Curada artesanalmente, con virola de alpaca. Capacidad 250ml.', 1500.00, 25, 'clasico'),
    ('Mate Imperial Palo Santo',  'Madera noble con aroma natural. Virola labrada a mano.',        3200.00,  8, 'premium'),
    ('Mate Camionero Jumbo',      'Gran capacidad 350ml. Ideal para largas jornadas.',             1800.00, 40, 'popular'),
    ('Mate Ceramico Artesanal',   'Pintado a mano por artesanos cordobeses. Edicion limitada.',   2400.00,  3, 'edicion limitada'),
    ('Termo Stanley 1L',          'Acero inoxidable. Mantiene temperatura 24hs.',                 8500.00, 15, 'accesorios'),
    ('Bombilla Alpaca Punta Cuchara', 'Alpaca 925. Corte perfecto para toda yerba.',              1200.00, 60, 'accesorios'),
    ('Mate Vidrio Transparente',  'Permite ver el nivel de agua. Con funda de cuero.',            2800.00,  0, 'premium'),
    ('Yerbera Ceramica',          'Set de 3 piezas. Ideal como regalo.',                          1900.00, 12, 'accesorios')
ON CONFLICT DO NOTHING;

-- ── USUARIO ADMIN DE PRUEBA ───────────────────────────────────
-- Contraseña: admin123  (hasheada con SHA-256 + salt por defecto)
-- IMPORTANTE: Cambia esta contraseña en produccion.
-- Para generar el hash con tu SECRET_SALT corri en Python:
--   import hmac, hashlib
--   hmac.new(b"cambia_esto_por_algo_muy_secreto_2025", b"admin123", hashlib.sha256).hexdigest()
INSERT INTO users (email, password_hash, full_name, role) VALUES
    (
        'admin@mateshop.com',
        -- Hash de "admin123" con salt "cambia_esto_por_algo_muy_secreto_2025"
        'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
        'Administrador',
        'admin'
    )
ON CONFLICT (email) DO NOTHING;

-- ── iNDICES ───────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_products_tag   ON products(tag);
CREATE INDEX IF NOT EXISTS idx_products_stock ON products(stock);
CREATE INDEX IF NOT EXISTS idx_users_email    ON users(email);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_mp_preference ON orders(mercado_pago_preference_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
