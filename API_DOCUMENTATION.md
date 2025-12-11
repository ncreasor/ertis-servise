# API Документация - Ertis Service (ЖКХ система)

## Описание

Система управления заявками ЖКХ с AI-анализом проблем и автоматическим распределением на сотрудников.

## Базовый URL

```
http://localhost:8000/api/v1
```

## Интерактивная документация

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## Аутентификация

### Регистрация пользователя

```http
POST /auth/register
Content-Type: application/json

{
  "first_name": "Иван",
  "last_name": "Иванов",
  "username": "ivan",
  "email": "ivan@example.com",
  "password": "password123"
}
```

### Вход (универсальный для всех ролей)

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=ivan&password=password123
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Получение информации о текущем пользователе

```http
GET /auth/me
Authorization: Bearer {access_token}
```

---

## Заявки (Requests)

### Создание заявки (для пользователей)

```http
POST /requests
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

description: "Прорвало трубу в квартире"
address: "г. Москва, ул. Ленина, д. 10, кв. 25"
category_id: 1
photo: [файл изображения]
```

**Процесс обработки:**
1. Фото сохраняется и оптимизируется
2. OpenAI GPT-4o-mini анализирует описание
3. OpenAI GPT-4o анализирует фото и определяет приоритет (1-5)
4. Система автоматически назначает заявку на подходящего сотрудника

### Получение своих заявок

```http
GET /requests/my
Authorization: Bearer {access_token}
```

### Получение назначенных заявок (для сотрудников)

```http
GET /requests/assigned
Authorization: Bearer {employee_access_token}
```

### Получение всех заявок с фильтрами (для админов ЖКХ)

```http
GET /requests?status=new&category_id=1&priority=5
Authorization: Bearer {admin_access_token}
```

**Параметры:**
- `status` - фильтр по статусу (new, assigned, in_progress, completed, spam, cancelled)
- `category_id` - фильтр по категории
- `priority` - фильтр по приоритету (1-5)

### Назначение заявки на сотрудника (для админов)

```http
PATCH /requests/{request_id}/assign
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "assignee_id": 5
}
```

### Завершение заявки с фото решения (для сотрудников)

```http
PATCH /requests/{request_id}/complete
Authorization: Bearer {employee_access_token}
Content-Type: multipart/form-data

solution_photo: [файл изображения]
```

### Закрытие заявки (для пользователей)

```http
PATCH /requests/{request_id}/close
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "completed"  // или "spam"
}
```

### Оценка работы сотрудника

```http
POST /requests/{request_id}/rate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "rating": 5,
  "comment": "Отличная работа, быстро устранили проблему",
  "request_id": 123
}
```

---

## Сотрудники (Employees)

### Создание сотрудника (для админов ЖКХ)

```http
POST /employees
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "first_name": "Петр",
  "last_name": "Петров",
  "username": "petr_plumber",
  "password": "password123",
  "specialty_id": 1,
  "organization_id": 1,
  "photo_url": null
}
```

### Получение списка сотрудников

```http
GET /employees?organization_id=1&specialty_id=2
Authorization: Bearer {admin_access_token}
```

### Получение информации о текущем сотруднике

```http
GET /employees/me
Authorization: Bearer {employee_access_token}
```

### Загрузка фото сотрудника

```http
POST /employees/{employee_id}/upload-photo
Authorization: Bearer {admin_access_token}
Content-Type: multipart/form-data

photo: [файл изображения]
```

---

## Категории (Categories)

### Получение всех категорий (доступно всем)

```http
GET /categories
```

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Водоснабжение",
    "description": "Проблемы с водопроводом, канализацией...",
    "created_at": "2024-01-01T00:00:00"
  },
  ...
]
```

### Создание категории (для админов)

```http
POST /categories
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "name": "Новая категория",
  "description": "Описание категории"
}
```

---

## Статистика (Statistics)

### Общая статистика (для админов ЖКХ)

```http
GET /statistics/overview
Authorization: Bearer {admin_access_token}
```

**Ответ:**
```json
{
  "total_requests": 150,
  "recent_requests_30_days": 45,
  "status_distribution": {
    "new": 10,
    "assigned": 15,
    "in_progress": 8,
    "completed": 100,
    "spam": 5,
    "cancelled": 12
  },
  "total_employees": 25,
  "average_employee_rating": 4.5,
  "average_completion_time_hours": 12.5,
  "requests_by_category": {
    "Водоснабжение": 50,
    "Электричество": 30,
    ...
  },
  "top_employees": [
    {
      "id": 5,
      "name": "Иван Иванов",
      "rating": 4.9
    },
    ...
  ]
}
```

### Статистика по сотруднику

```http
GET /statistics/employee/{employee_id}
Authorization: Bearer {admin_access_token}
```

### Распределение заявок по приоритетам

```http
GET /statistics/requests/priority
Authorization: Bearer {admin_access_token}
```

---

## Адреса (Addresses)

### Автокомплит адресов (Яндекс.Карты API)

```http
GET /addresses/suggest?query=Москва,%20Ленина
```

**Ответ:**
```json
{
  "query": "Москва, Ленина",
  "suggestions": [
    {
      "address": "Россия, Москва, улица Ленина, 10",
      "coordinates": {
        "latitude": 55.751244,
        "longitude": 37.618423
      }
    },
    ...
  ],
  "count": 10
}
```

### Геокодирование адреса

```http
GET /addresses/geocode?address=Москва,%20улица%20Ленина,%2010
```

---

## Роли и права доступа

### USER (Пользователь)
- Регистрация и вход
- Создание заявок
- Просмотр своих заявок
- Закрытие своих заявок
- Оценка работы сотрудников

### EMPLOYEE (Сотрудник ЖКХ)
- Вход
- Просмотр назначенных заявок
- Завершение заявок с фото решения
- Просмотр своего профиля

### HOUSING_ADMIN (Админ ЖКХ)
- Все права USER
- Создание и управление сотрудниками
- Просмотр всех заявок
- Назначение заявок на сотрудников
- Просмотр статистики
- Управление категориями

---

## Статусы заявок

- **NEW** - Новая заявка
- **ASSIGNED** - Назначена на сотрудника
- **IN_PROGRESS** - В работе
- **COMPLETED** - Завершена
- **SPAM** - Спам
- **CANCELLED** - Отменена

---

## Приоритеты заявок (определяются AI)

- **1** - Минимальный (косметические дефекты)
- **2** - Низкий (незначительные неудобства)
- **3** - Средний (требует внимания в течение недели)
- **4** - Высокий (серьезные неудобства)
- **5** - Критический (угроза безопасности, требует немедленного решения)

---

## Категории проблем (предустановленные)

1. **Водоснабжение** - Проблемы с водопроводом, канализацией
2. **Электричество** - Проблемы с электропроводкой, освещением
3. **Дорожное покрытие** - Ямы на дорогах, трещины асфальта
4. **Вывоз мусора** - Переполненные контейнеры
5. **Уборка территории** - Уборка снега, листьев, мусора
6. **Лифт** - Неисправности лифта
7. **Благоустройство** - Озеленение, детские площадки
8. **Отопление** - Проблемы с отоплением, батареями
9. **Подъезд** - Освещение, замки, домофон

---

## Коды ошибок

- **400** - Неверный запрос
- **401** - Не авторизован
- **403** - Недостаточно прав
- **404** - Не найдено
- **413** - Файл слишком большой
- **500** - Внутренняя ошибка сервера
- **503** - Сервис временно недоступен

---

## Примеры использования

### Пример полного цикла создания и выполнения заявки

1. **Регистрация пользователя**
2. **Вход и получение токена**
3. **Создание заявки с фото** - AI анализирует и определяет приоритет
4. **Система автоматически назначает заявку на сотрудника**
5. **Сотрудник входит и видит свою заявку**
6. **Сотрудник завершает заявку с фото решения**
7. **Пользователь оценивает работу сотрудника**
8. **Рейтинг сотрудника обновляется автоматически**

---

## Загрузка файлов

**Максимальный размер файла:** 10 MB
**Поддерживаемые форматы:** JPG, JPEG, PNG, GIF, WEBP
**Автоматическая оптимизация:** Да (максимальный размер изображения 2048x2048)

Загруженные файлы доступны по адресу:
```
http://localhost:8000/uploads/{subfolder}/{filename}
```

Подпапки:
- `requests/` - фотографии проблем
- `solutions/` - фотографии решений
- `employees/` - фотографии сотрудников
