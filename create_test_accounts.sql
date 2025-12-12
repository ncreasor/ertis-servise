-- ==========================================
-- SQL для создания тестовых аккаунтов
-- Выполнить в MySQL консоли Railway
-- ==========================================

-- Пароли захешированы bcrypt (все пароли: 123456)
-- Хеш для "123456": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qQJXhpbXHhWqGy

-- 1. Создаём администратора ЖКХ
INSERT INTO users (first_name, last_name, username, email, password_hash, role, created_at, updated_at)
VALUES (
    'Админ',
    'ЖКХ',
    'admin',
    'admin@ertis.kz',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qQJXhpbXHhWqGy',
    'admin',
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qQJXhpbXHhWqGy';

-- 2. Создаём второго администратора
INSERT INTO users (first_name, last_name, username, email, password_hash, role, created_at, updated_at)
VALUES (
    'Менеджер',
    'Системы',
    'manager',
    'manager@ertis.kz',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qQJXhpbXHhWqGy',
    'admin',
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qQJXhpbXHhWqGy';

-- 3. Создаём тестового жильца
INSERT INTO users (first_name, last_name, username, email, password_hash, role, created_at, updated_at)
VALUES (
    'Иван',
    'Иванов',
    'user',
    'user@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qQJXhpbXHhWqGy',
    'citizen',
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qQJXhpbXHhWqGy';

-- 4. Создаём тестового рабочего (сначала как пользователя)
INSERT INTO users (first_name, last_name, username, email, password_hash, role, created_at, updated_at)
VALUES (
    'Алексей',
    'Петров',
    'worker',
    'worker@ertis.kz',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qQJXhpbXHhWqGy',
    'employee',
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qQJXhpbXHhWqGy';

-- ==========================================
-- ТЕСТОВЫЕ АККАУНТЫ:
-- ==========================================
-- | Username | Password | Роль           |
-- |----------|----------|----------------|
-- | admin    | 123456   | Админ ЖКХ      |
-- | manager  | 123456   | Админ ЖКХ      |
-- | user     | 123456   | Житель         |
-- | worker   | 123456   | Рабочий        |
-- ==========================================

