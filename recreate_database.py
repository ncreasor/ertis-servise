#!/usr/bin/env python3
"""
Скрипт для пересоздания базы данных с правильными ENUM значениями
ВНИМАНИЕ: Удаляет все существующие данные!
"""
import asyncio
import sys

# Добавляем корневую директорию в путь
sys.path.insert(0, '.')

from app.core.database import engine, Base
from app.core.logging import get_logger

# Импортируем все модели для регистрации
from app.models.user import User
from app.models.employee import Employee
from app.models.category import Category
from app.models.specialty import Specialty
from app.models.request import Request
from app.models.notification import Notification
from app.models.rating import Rating

logger = get_logger()


async def recreate_database():
    """Пересоздание базы данных"""

    logger.info("=== Пересоздание базы данных ===\n")
    logger.warning("ВНИМАНИЕ: Все существующие данные будут удалены!")

    try:
        # Удаляем все таблицы
        logger.info("Удаление существующих таблиц...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("✓ Таблицы удалены")

        # Создаем таблицы заново
        logger.info("\nСоздание новых таблиц с правильными ENUM...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ Таблицы созданы")

        logger.info("\n✅ База данных успешно пересоздана!")
        logger.info("Все ENUM теперь используют значения в нижнем регистре:")
        logger.info("  - UserRole: citizen, employee, admin")
        logger.info("  - NotificationType: info, warning, success, error")
        logger.info("  - RequestStatus: pending, assigned, in_progress, completed, closed")
        logger.info("  - RequestPriority: low, medium, high")

    except Exception as e:
        logger.error(f"\n❌ Ошибка при пересоздании базы данных: {e}")
        raise


if __name__ == "__main__":
    # Подтверждение от пользователя
    print("\n" + "="*60)
    print("ВНИМАНИЕ: Этот скрипт удалит все данные из базы данных!")
    print("="*60)
    response = input("\nПродолжить? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        asyncio.run(recreate_database())
    else:
        print("Отменено пользователем")
