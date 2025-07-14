-- Расширение для генерации UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица гостей
CREATE TABLE IF NOT EXISTS guests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tg_id BIGINT UNIQUE,
    full_name TEXT,
    phone TEXT,
    birthdate TEXT,
    invited_at TIMESTAMP DEFAULT now()
);

-- Таблица посещений
CREATE TABLE IF NOT EXISTS visits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    guest_id UUID REFERENCES guests(id) ON DELETE CASCADE,
    visit_time TIMESTAMP DEFAULT now()
);

-- Таблица админов
CREATE TABLE IF NOT EXISTS admins (
    user_id BIGINT PRIMARY KEY
);
