# Исправление ENUM на Railway

## Проблема
SQLAlchemy при создании ENUM в MySQL использовал имена enum членов (CITIZEN, EMPLOYEE, ADMIN) вместо их значений (citizen, employee, admin).

## Что было исправлено в коде

✅ Все ENUM теперь используют `values_callable` для правильной генерации значений:

1. **app/models/user.py:27** - UserRole (citizen, employee, admin)
2. **app/models/notification.py:26** - NotificationType (info, warning, success, error)
3. **app/models/request.py:47-48** - RequestStatus и RequestPriority

## Как применить изменения на Railway

### Вариант 1: Пересоздать базу данных (рекомендуется для dev)

**ВНИМАНИЕ: Удалит все данные!**

1. Зайдите на [railway.app](https://railway.app)
2. Откройте ваш проект
3. Перейдите в сервис **MySQL**
4. Нажмите **"Settings"** → **"Danger"** → **"Delete Service"**
5. Создайте новую базу данных: **"+ New"** → **"Database"** → **"Add MySQL"**
6. Проверьте, что переменная `DATABASE_URL` обновилась и имеет формат `mysql+aiomysql://...`
7. Передеплойте приложение (Railway сделает это автоматически)

### Вариант 2: Выполнить SQL миграцию (сохраняет данные)

#### Через Railway Shell:

1. Зайдите на railway.app
2. Откройте ваш проект
3. Откройте сервис с приложением
4. Перейдите в **"Settings"** → **"Environment"**
5. Скопируйте переменную `DATABASE_URL`
6. В терминале подключитесь к базе:
   ```bash
   # Установите Railway CLI (если не установлен)
   npm install -g @railway/cli

   # Войдите в аккаунт
   railway login

   # Подключитесь к проекту
   railway link

   # Выполните SQL скрипт
   railway run mysql -u [username] -p[password] -h [host] -P [port] [database] < fix_enum_values.sql
   ```

#### Через MySQL клиент (рекомендуется):

1. Используйте любой MySQL клиент (MySQL Workbench, DBeaver, phpMyAdmin)
2. Подключитесь к Railway MySQL используя данные из `DATABASE_URL`
3. Выполните SQL команды из файла `fix_enum_values.sql` (3 шага):

**ШАГ 1:** Расширяем ENUM для временного включения старых значений
```sql
ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin', 'CITIZEN', 'EMPLOYEE', 'ADMIN') DEFAULT 'citizen' NOT NULL;
ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error', 'INFO', 'WARNING', 'SUCCESS', 'ERROR') DEFAULT 'info' NOT NULL;
ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed', 'PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED') DEFAULT 'pending' NOT NULL;
ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high', 'LOW', 'MEDIUM', 'HIGH') DEFAULT 'medium' NOT NULL;
```

**ШАГ 2:** Обновляем все существующие данные на нижний регистр
```sql
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
```

**ШАГ 3:** Удаляем старые значения из ENUM (оставляем только нижний регистр)
```sql
ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin') DEFAULT 'citizen' NOT NULL;
ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error') DEFAULT 'info' NOT NULL;
ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed') DEFAULT 'pending' NOT NULL;
ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high') DEFAULT 'medium' NOT NULL;
```

### Вариант 3: Через Python скрипт (сохраняет данные)

1. Закоммитьте и запушьте изменения в Git:
   ```bash
   git add .
   git commit -m "fix: Update ENUM values to use lowercase"
   git push
   ```

2. Railway автоматически передеплоит приложение

3. Подключитесь к Railway Shell:
   ```bash
   railway run python fix_enum_migration.py
   ```

## Проверка исправления

После применения одного из вариантов, попробуйте зарегистрировать пользователя через API:

```bash
curl -X POST "https://your-railway-url/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Тест",
    "last_name": "Тестов",
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

Если регистрация прошла успешно - проблема решена! ✅

## Локальное тестирование

Если вы тестируете локально, используйте:

```bash
# Активируйте виртуальное окружение
source venv/bin/activate  # или на Windows: venv\Scripts\activate

# Пересоздайте базу данных
python recreate_database.py

# Запустите сервер
python run.py
```
