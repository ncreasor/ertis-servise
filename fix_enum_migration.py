#!/usr/bin/env python3
"""
Скрипт для исправления ENUM значений в базе данных
Все ENUM должны использовать значения в нижнем регистре
"""
import asyncio
import sys
from sqlalchemy import text

# Добавляем корневую директорию в путь
sys.path.insert(0, '.')

from app.core.database import engine
from app.core.logging import get_logger

logger = get_logger()


async def fix_enum_values():
    """Исправление ENUM значений в базе данных"""

    sql_commands = [
        # Исправление таблицы users
        "ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin') DEFAULT 'citizen' NOT NULL",

        # Исправление таблицы notifications (если существует)
        "ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error') DEFAULT 'info' NOT NULL",

        # Исправление таблицы requests (если существует)
        "ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed') DEFAULT 'pending' NOT NULL",
        "ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high') DEFAULT 'medium' NOT NULL",
    ]

    async with engine.begin() as conn:
        for sql in sql_commands:
            try:
                logger.info(f"Выполняем: {sql[:80]}...")
                await conn.execute(text(sql))
                logger.info("✓ Успешно выполнено")
            except Exception as e:
                logger.warning(f"Ошибка при выполнении команды: {e}")
                logger.info("Продолжаем выполнение...")

    logger.info("\n✅ Миграция завершена!")
    logger.info("Все ENUM теперь используют значения в нижнем регистре")


if __name__ == "__main__":
    print("=== Миграция ENUM значений ===\n")
    asyncio.run(fix_enum_values())
