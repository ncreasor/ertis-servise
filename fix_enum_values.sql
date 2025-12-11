-- Скрипт для исправления ENUM значений в базе данных
-- Все ENUM должны использовать значения в нижнем регистре

-- ШАГ 1: Расширяем ENUM для включения обоих вариантов (старый и новый)
ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin', 'CITIZEN', 'EMPLOYEE', 'ADMIN') DEFAULT 'citizen' NOT NULL;
ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error', 'INFO', 'WARNING', 'SUCCESS', 'ERROR') DEFAULT 'info' NOT NULL;
ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed', 'PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED') DEFAULT 'pending' NOT NULL;
ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high', 'LOW', 'MEDIUM', 'HIGH') DEFAULT 'medium' NOT NULL;

-- ШАГ 2: Обновляем существующие данные на нижний регистр
UPDATE users SET role = 'citizen' WHERE role = 'CITIZEN';
UPDATE users SET role = 'employee' WHERE role = 'EMPLOYEE';
UPDATE users SET role = 'admin' WHERE role = 'ADMIN';

UPDATE notifications SET type = 'info' WHERE type = 'INFO';
UPDATE notifications SET type = 'warning' WHERE type = 'WARNING';
UPDATE notifications SET type = 'success' WHERE type = 'SUCCESS';
UPDATE notifications SET type = 'error' WHERE type = 'ERROR';

UPDATE requests SET status = 'pending' WHERE status = 'PENDING';
UPDATE requests SET status = 'assigned' WHERE status = 'ASSIGNED';
UPDATE requests SET status = 'in_progress' WHERE status = 'IN_PROGRESS';
UPDATE requests SET status = 'completed' WHERE status = 'COMPLETED';
UPDATE requests SET status = 'closed' WHERE status = 'CLOSED';

UPDATE requests SET priority = 'low' WHERE priority = 'LOW';
UPDATE requests SET priority = 'medium' WHERE priority = 'MEDIUM';
UPDATE requests SET priority = 'high' WHERE priority = 'HIGH';

-- ШАГ 3: Удаляем старые значения из ENUM (оставляем только нижний регистр)
ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin') DEFAULT 'citizen' NOT NULL;
ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error') DEFAULT 'info' NOT NULL;
ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed') DEFAULT 'pending' NOT NULL;
ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high') DEFAULT 'medium' NOT NULL;
