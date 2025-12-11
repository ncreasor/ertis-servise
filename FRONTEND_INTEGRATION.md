# Интеграция Фронтенда - Изменения в Бэкенде

## ✅ Все несоответствия исправлены!

### 📋 Список изменений:

---

## 1. **User Model & Authentication**

### Изменения:
- ✅ Добавлены поля: `phone` (обязательное), `middle_name` (опциональное), `is_active`
- ✅ Изменены роли: `user` → `citizen`, `housing_admin` → `admin`
- ✅ Email теперь обязательное поле

### Эндпоинты:
- **POST /api/v1/auth/register** - теперь требует `{email, password, username, first_name, last_name, phone, middle_name?}` и возвращает `{access_token, token_type, user}`
- **POST /api/v1/auth/login** - теперь принимает `{email, password}` (не username!) и возвращает `{access_token, token_type, user}`

---

## 2. **Request Model & Endpoints**

### Изменения модели:
- ✅ Добавлены поля: `title`, `problem_type`, `latitude`, `longitude`, `ai_category`, `ai_description`, `completion_note`
- ✅ Переименовано: `solution_photo_url` → `completion_photo_url`
- ✅ Изменены статусы: `NEW` → `PENDING`, `SPAM`/`CANCELLED` → `CLOSED`
- ✅ Изменен приоритет: числа 1-5 → строки "low"/"medium"/"high"

### Эндпоинты:

#### **POST /api/v1/requests** (создание заявки)
- Было: `category_id` (int), `photo` (обязательное)
- Стало: `category` (string), `problem_type?`, `latitude?`, `longitude?`, `photo?` (опциональное)

#### **PATCH /api/v1/requests/{id}/complete** (завершение)
- Было: `solution_photo` (обязательное)
- Стало: `completion_photo?`, `completion_note?` (оба опциональные)

#### **PATCH /api/v1/requests/{id}/close** (закрытие)
- Было: `{status: "completed" | "spam"}`
- Стало: `{reason?: string}` - закрывает со статусом CLOSED

#### **PATCH /api/v1/requests/{id}/assign** (назначение)
- Теперь принимает как `employee_id`, так и `assignee_id` (совместимость)

#### **POST /api/v1/requests/{id}/rate** (оценка)
- Удален обязательный `request_id` из body (уже в URL)

### RequestResponse (ответ API):
```typescript
{
  id: number,
  user_id: number,  // вместо creator_id
  assigned_employee_id?: number,  // вместо assignee_id
  category_id?: number,
  title?: string,
  description: string,
  problem_type?: string,
  address: string,
  latitude?: number,
  longitude?: number,
  photo_url?: string,
  completion_photo_url?: string,  // вместо solution_photo_url
  completion_note?: string,
  status: "pending" | "assigned" | "in_progress" | "completed" | "closed",
  priority: "low" | "medium" | "high",
  ai_category?: string,
  ai_description?: string,
  completed_at?: string,
  created_at: string,
  updated_at: string
}
```

---

## 3. **Notifications** (новое!)

### Добавлены эндпоинты:
- **GET /api/v1/notifications** - получить все уведомления пользователя
- **PUT /api/v1/notifications/{id}/read** - пометить уведомление как прочитанное

### NotificationResponse:
```typescript
{
  id: number,
  user_id: number,
  title: string,
  message: string,
  type: "info" | "warning" | "success" | "error",
  is_read: boolean,
  created_at: string
}
```

---

## 4. **Роли пользователей**

Изменены значения enum:
- ~~`user`~~ → **`citizen`**
- ~~`housing_admin`~~ → **`admin`**
- `employee` - без изменений

---

## 🔧 Что нужно сделать:

### 1. **Обновить базу данных**

Так как изменилась структура моделей, нужно **пересоздать БД**:

```bash
# Удали старую БД в phpMyAdmin или через командную строку
mysql -u root -p -e "DROP DATABASE IF EXISTS ertis_db; CREATE DATABASE ertis_db;"

# Запусти бэкенд - таблицы создадутся автоматически
python run.py
```

### 2. **Обновить .env файл**

Добавь Vercel домен фронта в ALLOWED_ORIGINS:

```env
ALLOWED_ORIGINS=http://localhost:3000,https://твой-фронт.vercel.app
```

### 3. **Запушить изменения в GitHub**

```bash
git add .
git commit -m "Fix: Adapt backend for frontend integration

- Add phone & middle_name to User model
- Change roles: citizen/employee/admin
- Update Request model: add title, problem_type, coordinates, AI fields
- Rename solution_photo_url to completion_photo_url
- Change priority from numbers to low/medium/high
- Add /notifications endpoints
- Fix all endpoint parameters to match frontend API client"

git push origin main
```

Railway автоматически сделает redeploy.

### 4. **Обновить Railway переменные окружения**

В Railway Dashboard → Variables:

1. Убедись что `DATABASE_URL` имеет префикс `mysql+aiomysql://`
2. Добавь Vercel домен в `ALLOWED_ORIGINS`:
   ```
   http://localhost:3000,https://твой-фронт.vercel.app
   ```

---

## 📄 Полная совместимость с фронтом

Теперь бэк полностью совместим с фронтом из `Front_Ertis/src/lib/api.ts`:

✅ Login через email
✅ Register с phone и middle_name
✅ AuthResponse с user объектом
✅ Request с category (string) вместо category_id
✅ Notifications эндпоинты
✅ completion_photo вместо solution_photo
✅ employee_id поддержка в assignRequest
✅ Приоритет как строка (low/medium/high)

---

## 🚀 Готово к деплою!

После выполнения шагов выше:
1. Фронт на Vercel будет работать с бэком на Railway
2. Все API эндпоинты будут совместимы
3. Swagger документация обновится автоматически

Удачи на хакатоне! 🔥
