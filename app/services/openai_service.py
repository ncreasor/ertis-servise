"""
Сервис для работы с OpenAI API
"""
import base64
from typing import Optional
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def analyze_problem_description(description: str, category_name: str) -> str:
    """
    Обработка описания проблемы с помощью gpt-4o-mini
    Формирует структурированное описание для анализа фото
    """
    try:
        prompt = f"""
Ты - помощник системы управления заявками ЖКХ.

Категория проблемы: {category_name}
Описание проблемы от пользователя: {description}

Твоя задача:
1. Проанализируй описание проблемы
2. Создай структурированное описание для AI-анализа фотографии
3. Укажи ключевые признаки, которые нужно найти на фото

Формат ответа должен быть кратким и конкретным, перечисли 3-5 ключевых признаков проблемы.
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты - эксперт по анализу проблем в жилищно-коммунальном хозяйстве."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )

        structured_description = response.choices[0].message.content
        logger.info(f"Обработано описание проблемы: {structured_description[:100]}...")

        return structured_description

    except Exception as e:
        logger.error(f"Ошибка при обработке описания: {e}")
        return description  # Возвращаем оригинальное описание в случае ошибки


async def analyze_image_priority(
    image_path: str,
    structured_description: str,
    category_name: str
) -> str:
    """
    Анализ изображения и определение приоритета проблемы (low/medium/high)
    Использует gpt-4o для анализа изображения
    """
    try:
        # Читаем изображение и конвертируем в base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        prompt = f"""
Ты - эксперт по оценке проблем в жилищно-коммунальном хозяйстве.

Категория: {category_name}
Описание проблемы: {structured_description}

Проанализируй фотографию и определи ПРИОРИТЕТ проблемы:

low - Низкий (косметические дефекты, незначительные неудобства, можно отложить)
medium - Средний (требует внимания в течение недели, создает неудобства)
high - Высокий (серьезная проблема, угроза безопасности/здоровью, требует срочного решения)

Учитывай:
- Степень повреждения/проблемы
- Потенциальную опасность для людей
- Влияние на комфорт проживания
- Возможные последствия если не решить

Ответь ТОЛЬКО одним словом: low, medium или high, без пояснений.
"""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=10,
            temperature=0.1
        )

        priority_str = response.choices[0].message.content.strip().lower()

        # Валидация ответа
        valid_priorities = ["low", "medium", "high"]
        if priority_str not in valid_priorities:
            logger.warning(f"Некорректный приоритет '{priority_str}', используем 'medium'")
            priority_str = "medium"

        logger.info(f"Определен приоритет: {priority_str}")
        return priority_str

    except Exception as e:
        logger.error(f"Ошибка при анализе изображения: {e}")
        return "medium"  # В случае ошибки возвращаем средний приоритет


async def generate_user_recommendation(
    description: str,
    category_name: str,
    priority: str
) -> str:
    """
    Генерация краткой рекомендации для пользователя по его заявке.
    Возвращает понятное сообщение о статусе обработки.
    """
    try:
        prompt = f"""
Ты - помощник системы ЖКХ города Павлодар.

Пользователь подал заявку:
- Категория: {category_name}
- Описание: {description}
- Определенный приоритет: {priority}

Сформируй КРАТКУЮ рекомендацию (2-3 предложения) для пользователя:
1. Подтверди что заявка принята
2. Кратко опиши что будет сделано
3. Укажи примерные сроки исходя из приоритета (high = срочно/сегодня, medium = 1-3 дня, low = до недели)

Пиши дружелюбно, на русском языке. Не используй технические термины.
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты - дружелюбный помощник ЖКХ. Отвечай кратко и понятно."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        recommendation = response.choices[0].message.content.strip()
        logger.info(f"Сгенерирована рекомендация: {recommendation[:50]}...")
        return recommendation

    except Exception as e:
        logger.error(f"Ошибка при генерации рекомендации: {e}")
        # Дефолтное сообщение
        priority_text = {
            "high": "Ваша заявка имеет высокий приоритет и будет обработана в ближайшее время.",
            "medium": "Ваша заявка принята и будет обработана в течение 1-3 рабочих дней.",
            "low": "Ваша заявка принята и будет обработана в течение недели."
        }
        return priority_text.get(priority, "Ваша заявка принята и находится в обработке.")


async def assign_employee_ai(
    request_description: str,
    category_name: str,
    priority: int,
    available_employees: list[dict]
) -> Optional[int]:
    """
    Автоматическое распределение заявки на сотрудника с помощью AI

    Args:
        request_description: Описание заявки
        category_name: Категория проблемы
        priority: Приоритет заявки
        available_employees: Список доступных сотрудников с информацией
            [{"id": int, "name": str, "specialty": str, "rating": float, "active_requests": int}, ...]

    Returns:
        ID выбранного сотрудника или None
    """
    if not available_employees:
        logger.warning("Нет доступных сотрудников для распределения")
        return None

    try:
        employees_info = "\n".join([
            f"- ID: {emp['id']}, Имя: {emp['name']}, Специальность: {emp['specialty']}, "
            f"Рейтинг: {emp['rating']:.1f}/5.0, Активных заявок: {emp['active_requests']}"
            for emp in available_employees
        ])

        prompt = f"""
Ты - система автоматического распределения заявок в ЖКХ.

ЗАЯВКА:
Категория: {category_name}
Приоритет: {priority}/5
Описание: {request_description}

ДОСТУПНЫЕ СОТРУДНИКИ:
{employees_info}

Выбери ОДНОГО наиболее подходящего сотрудника, учитывая:
1. Специальность должна соответствовать категории проблемы
2. Рейтинг сотрудника (выше - лучше)
3. Текущая загрузка (меньше активных заявок - лучше)
4. Для критических проблем (приоритет 4-5) выбирай сотрудников с высоким рейтингом

Ответь ТОЛЬКО ID выбранного сотрудника (одно число), без пояснений.
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты - система распределения задач. Отвечай только цифрой."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.2
        )

        employee_id_str = response.choices[0].message.content.strip()

        try:
            employee_id = int(employee_id_str)
            # Проверяем что такой сотрудник есть в списке
            if employee_id in [emp["id"] for emp in available_employees]:
                logger.info(f"AI выбрал сотрудника ID: {employee_id}")
                return employee_id
            else:
                logger.warning(f"AI вернул невалидный ID: {employee_id}")
                # Возвращаем сотрудника с наименьшей загрузкой и высоким рейтингом
                best_employee = min(available_employees, key=lambda x: (x["active_requests"], -x["rating"]))
                return best_employee["id"]
        except ValueError:
            logger.warning(f"Не удалось распарсить ID сотрудника: {employee_id_str}")
            # Возвращаем сотрудника с наименьшей загрузкой
            best_employee = min(available_employees, key=lambda x: x["active_requests"])
            return best_employee["id"]

    except Exception as e:
        logger.error(f"Ошибка при автоматическом распределении: {e}")
        # В случае ошибки возвращаем сотрудника с наименьшей загрузкой
        if available_employees:
            best_employee = min(available_employees, key=lambda x: x["active_requests"])
            return best_employee["id"]
        return None
