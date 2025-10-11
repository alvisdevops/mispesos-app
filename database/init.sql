-- MisPesos Database Schema
-- PostgreSQL 15+

-- ========================================
-- 1. CATEGORIES TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,

    -- Category information
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3B82F6',
    icon VARCHAR(50),

    -- Classification settings
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 0,

    -- AI learning metadata
    ai_usage_count INTEGER DEFAULT 0,
    accuracy_score FLOAT DEFAULT 0.0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_categories_is_active ON categories(is_active);

-- ========================================
-- 2. CATEGORY KEYWORDS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS category_keywords (
    id SERIAL PRIMARY KEY,

    -- Foreign key
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,

    -- Keyword data
    keyword VARCHAR(100) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,

    -- Learning metadata
    match_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_keywords_keyword ON category_keywords(keyword);
CREATE INDEX idx_keywords_category ON category_keywords(category_id);
CREATE INDEX idx_keywords_is_active ON category_keywords(is_active);

-- ========================================
-- 3. TRANSACTIONS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,

    -- Financial data
    amount FLOAT NOT NULL,
    description VARCHAR(500) NOT NULL,

    -- Classification
    category_id INTEGER REFERENCES categories(id),
    payment_method VARCHAR(50) NOT NULL,

    -- Metadata
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    location VARCHAR(200),

    -- AI processing metadata
    ai_confidence FLOAT,
    ai_model_used VARCHAR(50),
    original_text TEXT,

    -- Telegram integration
    telegram_message_id BIGINT,
    telegram_user_id BIGINT NOT NULL,

    -- Status and validation
    is_validated BOOLEAN DEFAULT FALSE,
    is_correction BOOLEAN DEFAULT FALSE,
    corrected_transaction_id INTEGER REFERENCES transactions(id),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_user ON transactions(telegram_user_id);
CREATE INDEX idx_transactions_telegram_msg ON transactions(telegram_message_id);

-- ========================================
-- 4. RECEIPTS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS receipts (
    id SERIAL PRIMARY KEY,

    -- Foreign key (1:1 with transaction)
    transaction_id INTEGER NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,

    -- File information
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(10) NOT NULL,

    -- OCR processing
    ocr_text TEXT,
    ocr_confidence FLOAT,
    ocr_engine VARCHAR(50) DEFAULT 'tesseract',

    -- AI processing
    ai_extracted_data JSON,
    ai_confidence FLOAT,
    ai_model_used VARCHAR(50),

    -- Fiscal information
    company_name VARCHAR(200),
    company_nit VARCHAR(20),
    receipt_number VARCHAR(50),
    receipt_date TIMESTAMP WITH TIME ZONE,

    -- Tax information
    subtotal FLOAT,
    tax_amount FLOAT,
    tax_percentage FLOAT,
    total_amount FLOAT,

    -- Processing status
    is_processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,
    needs_review BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_receipts_transaction ON receipts(transaction_id);
CREATE INDEX idx_receipts_processed ON receipts(is_processed);

-- ========================================
-- SEED DATA: CATEGORIES
-- ========================================
INSERT INTO categories (name, description, color, icon, is_system, priority) VALUES
('Alimentación', 'Comida, restaurantes, supermercado, snacks', '#FF6B6B', '🍽️', TRUE, 10),
('Transporte', 'Uber, taxi, gasolina, buses, parqueadero', '#4ECDC4', '🚗', TRUE, 9),
('Servicios', 'Internet, teléfono, luz, agua, streaming', '#45B7D1', '⚡', TRUE, 8),
('Salud', 'Médicos, medicinas, seguros médicos, farmacias', '#96CEB4', '🏥', TRUE, 7),
('Entretenimiento', 'Cine, teatro, bares, conciertos, eventos', '#FFEAA7', '🎭', TRUE, 6),
('Ropa', 'Vestimenta, calzado, accesorios', '#DFE6E9', '👕', TRUE, 5),
('Educación', 'Cursos, libros, materiales educativos', '#A29BFE', '📚', TRUE, 4),
('Hogar', 'Limpieza, decoración, mantenimiento', '#FD79A8', '🏠', TRUE, 3),
('Otros', 'Gastos varios no clasificados', '#B2BEC3', '📦', TRUE, 1)
ON CONFLICT (name) DO NOTHING;

-- ========================================
-- SEED DATA: CATEGORY KEYWORDS
-- ========================================

-- Alimentación keywords
INSERT INTO category_keywords (category_id, keyword, weight) VALUES
((SELECT id FROM categories WHERE name = 'Alimentación'), 'almuerzo', 1.0),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'desayuno', 1.0),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'cena', 1.0),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'comida', 1.0),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'restaurante', 1.0),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'pizza', 0.9),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'hamburguesa', 0.9),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'café', 0.8),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'supermercado', 1.0),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'super', 1.0),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'mercado', 1.0),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'lonche', 0.9),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'mecato', 0.8),
((SELECT id FROM categories WHERE name = 'Alimentación'), 'rappi', 0.7);

-- Transporte keywords
INSERT INTO category_keywords (category_id, keyword, weight) VALUES
((SELECT id FROM categories WHERE name = 'Transporte'), 'uber', 1.0),
((SELECT id FROM categories WHERE name = 'Transporte'), 'taxi', 1.0),
((SELECT id FROM categories WHERE name = 'Transporte'), 'bus', 0.9),
((SELECT id FROM categories WHERE name = 'Transporte'), 'gasolina', 1.0),
((SELECT id FROM categories WHERE name = 'Transporte'), 'metro', 0.9),
((SELECT id FROM categories WHERE name = 'Transporte'), 'parqueadero', 0.9),
((SELECT id FROM categories WHERE name = 'Transporte'), 'didi', 1.0),
((SELECT id FROM categories WHERE name = 'Transporte'), 'cabify', 1.0),
((SELECT id FROM categories WHERE name = 'Transporte'), 'transmilenio', 0.9),
((SELECT id FROM categories WHERE name = 'Transporte'), 'peaje', 0.8);

-- Servicios keywords
INSERT INTO category_keywords (category_id, keyword, weight) VALUES
((SELECT id FROM categories WHERE name = 'Servicios'), 'internet', 1.0),
((SELECT id FROM categories WHERE name = 'Servicios'), 'teléfono', 1.0),
((SELECT id FROM categories WHERE name = 'Servicios'), 'celular', 1.0),
((SELECT id FROM categories WHERE name = 'Servicios'), 'luz', 1.0),
((SELECT id FROM categories WHERE name = 'Servicios'), 'agua', 1.0),
((SELECT id FROM categories WHERE name = 'Servicios'), 'gas', 1.0),
((SELECT id FROM categories WHERE name = 'Servicios'), 'netflix', 0.9),
((SELECT id FROM categories WHERE name = 'Servicios'), 'spotify', 0.9),
((SELECT id FROM categories WHERE name = 'Servicios'), 'prime', 0.9),
((SELECT id FROM categories WHERE name = 'Servicios'), 'streaming', 0.8);

-- Salud keywords
INSERT INTO category_keywords (category_id, keyword, weight) VALUES
((SELECT id FROM categories WHERE name = 'Salud'), 'médico', 1.0),
((SELECT id FROM categories WHERE name = 'Salud'), 'doctor', 1.0),
((SELECT id FROM categories WHERE name = 'Salud'), 'medicina', 1.0),
((SELECT id FROM categories WHERE name = 'Salud'), 'farmacia', 1.0),
((SELECT id FROM categories WHERE name = 'Salud'), 'drogas', 1.0),
((SELECT id FROM categories WHERE name = 'Salud'), 'consulta', 0.9),
((SELECT id FROM categories WHERE name = 'Salud'), 'hospital', 1.0),
((SELECT id FROM categories WHERE name = 'Salud'), 'seguro', 0.8);

-- Entretenimiento keywords
INSERT INTO category_keywords (category_id, keyword, weight) VALUES
((SELECT id FROM categories WHERE name = 'Entretenimiento'), 'cine', 1.0),
((SELECT id FROM categories WHERE name = 'Entretenimiento'), 'teatro', 1.0),
((SELECT id FROM categories WHERE name = 'Entretenimiento'), 'concierto', 1.0),
((SELECT id FROM categories WHERE name = 'Entretenimiento'), 'bar', 0.9),
((SELECT id FROM categories WHERE name = 'Entretenimiento'), 'discoteca', 0.9),
((SELECT id FROM categories WHERE name = 'Entretenimiento'), 'rumba', 0.9),
((SELECT id FROM categories WHERE name = 'Entretenimiento'), 'pola', 0.8),
((SELECT id FROM categories WHERE name = 'Entretenimiento'), 'cerveza', 0.8);

-- Ropa keywords
INSERT INTO category_keywords (category_id, keyword, weight) VALUES
((SELECT id FROM categories WHERE name = 'Ropa'), 'ropa', 1.0),
((SELECT id FROM categories WHERE name = 'Ropa'), 'camisa', 0.9),
((SELECT id FROM categories WHERE name = 'Ropa'), 'pantalón', 0.9),
((SELECT id FROM categories WHERE name = 'Ropa'), 'zapatos', 0.9),
((SELECT id FROM categories WHERE name = 'Ropa'), 'tenis', 0.9);

-- Educación keywords
INSERT INTO category_keywords (category_id, keyword, weight) VALUES
((SELECT id FROM categories WHERE name = 'Educación'), 'curso', 1.0),
((SELECT id FROM categories WHERE name = 'Educación'), 'libro', 0.9),
((SELECT id FROM categories WHERE name = 'Educación'), 'universidad', 1.0),
((SELECT id FROM categories WHERE name = 'Educación'), 'matrícula', 1.0);

-- Hogar keywords
INSERT INTO category_keywords (category_id, keyword, weight) VALUES
((SELECT id FROM categories WHERE name = 'Hogar'), 'limpieza', 1.0),
((SELECT id FROM categories WHERE name = 'Hogar'), 'hogar', 1.0),
((SELECT id FROM categories WHERE name = 'Hogar'), 'casa', 0.9),
((SELECT id FROM categories WHERE name = 'Hogar'), 'arriendo', 1.0),
((SELECT id FROM categories WHERE name = 'Hogar'), 'alquiler', 1.0);

-- ========================================
-- COMPLETION MESSAGE
-- ========================================
DO $$
BEGIN
    RAISE NOTICE '✅ Database initialized successfully!';
    RAISE NOTICE '📊 Tables created: categories, category_keywords, transactions, receipts';
    RAISE NOTICE '🏷️  Categories loaded: 9';
    RAISE NOTICE '🔑 Keywords loaded: %', (SELECT COUNT(*) FROM category_keywords);
END $$;
