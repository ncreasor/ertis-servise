-- Скрипт для обновления существующих данных в нижний регистр

-- Обновляем роли пользователей
UPDATE users SET role = 'citizen' WHERE role = 'CITIZEN';
UPDATE users SET role = 'employee' WHERE role = 'EMPLOYEE';
UPDATE users SET role = 'admin' WHERE role = 'ADMIN';

-- Обновляем типы уведомлений (если есть данные)
UPDATE notifications SET type = 'info' WHERE type = 'INFO';
UPDATE notifications SET type = 'warning' WHERE type = 'WARNING';
UPDATE notifications SET type = 'success' WHERE type = 'SUCCESS';
UPDATE notifications SET type = 'error' WHERE type = 'ERROR';

-- Обновляем статусы заявок (если есть данные)
UPDATE requests SET status = 'pending' WHERE status = 'PENDING';
UPDATE requests SET status = 'assigned' WHERE status = 'ASSIGNED';
UPDATE requests SET status = 'in_progress' WHERE status = 'IN_PROGRESS';
UPDATE requests SET status = 'completed' WHERE status = 'COMPLETED';
UPDATE requests SET status = 'closed' WHERE status = 'CLOSED';

-- Обновляем приоритеты заявок (если есть данные)
UPDATE requests SET priority = 'low' WHERE priority = 'LOW';
UPDATE requests SET priority = 'medium' WHERE priority = 'MEDIUM';
UPDATE requests SET priority = 'high' WHERE priority = 'HIGH';
