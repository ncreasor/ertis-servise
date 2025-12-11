-- Скрипт для исправления ENUM значений в базе данных
-- Все ENUM должны использовать значения в нижнем регистре

-- Исправление таблицы users
ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin') DEFAULT 'citizen' NOT NULL;

-- Исправление таблицы notifications (если существует)
ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error') DEFAULT 'info' NOT NULL;

-- Исправление таблицы requests (если существует)
ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed') DEFAULT 'pending' NOT NULL;
ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high') DEFAULT 'medium' NOT NULL;
