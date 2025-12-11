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

    # Шаг 1: Изменяем ENUM колонки
    alter_commands = [
        # Исправление таблицы users
        "ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin', 'CITIZEN', 'EMPLOYEE', 'ADMIN') DEFAULT 'citizen' NOT NULL",

        # Исправление таблицы notifications (если существует)
        "ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error', 'INFO', 'WARNING', 'SUCCESS', 'ERROR') DEFAULT 'info' NOT NULL",

        # Исправление таблицы requests (если существует)
        "ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed', 'PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED') DEFAULT 'pending' NOT NULL",
        "ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high', 'LOW', 'MEDIUM', 'HIGH') DEFAULT 'medium' NOT NULL",
    ]

    # Шаг 2: Обновляем существующие данные
    update_commands = [
        # Обновляем роли пользователей
        "UPDATE users SET role = 'citizen' WHERE role = 'CITIZEN'",
        "UPDATE users SET role = 'employee' WHERE role = 'EMPLOYEE'",
        "UPDATE users SET role = 'admin' WHERE role = 'ADMIN'",

        # Обновляем типы уведомлений
        "UPDATE notifications SET type = 'info' WHERE type = 'INFO'",
        "UPDATE notifications SET type = 'warning' WHERE type = 'WARNING'",
        "UPDATE notifications SET type = 'success' WHERE type = 'SUCCESS'",
        "UPDATE notifications SET type = 'error' WHERE type = 'ERROR'",

        # Обновляем статусы заявок
        "UPDATE requests SET status = 'pending' WHERE status = 'PENDING'",
        "UPDATE requests SET status = 'assigned' WHERE status = 'ASSIGNED'",
        "UPDATE requests SET status = 'in_progress' WHERE status = 'IN_PROGRESS'",
        "UPDATE requests SET status = 'completed' WHERE status = 'COMPLETED'",
        "UPDATE requests SET status = 'closed' WHERE status = 'CLOSED'",

        # Обновляем приоритеты заявок
        "UPDATE requests SET priority = 'low' WHERE priority = 'LOW'",
        "UPDATE requests SET priority = 'medium' WHERE priority = 'MEDIUM'",
        "UPDATE requests SET priority = 'high' WHERE priority = 'HIGH'",
    ]

    # Шаг 3: Удаляем старые значения из ENUM
    final_alter_commands = [
        "ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin') DEFAULT 'citizen' NOT NULL",
        "ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error') DEFAULT 'info' NOT NULL",
        "ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed') DEFAULT 'pending' NOT NULL",
        "ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high') DEFAULT 'medium' NOT NULL",
    ]

    async with engine.begin() as conn:
        logger.info("Шаг 1: Расширяем ENUM для включения старых значений...")
        for sql in alter_commands:
            try:
                await conn.execute(text(sql))
                logger.info("✓ OK")
            except Exception as e:
                logger.warning(f"⚠ {e}")

        logger.info("\nШаг 2: Обновляем существующие данные...")
        for sql in update_commands:
            try:
                result = await conn.execute(text(sql))
                if result.rowcount > 0:
                    logger.info(f"✓ Обновлено {result.rowcount} строк")
            except Exception as e:
                logger.warning(f"⚠ {e}")

        logger.info("\nШаг 3: Удаляем старые значения из ENUM...")
        for sql in final_alter_commands:
            try:
                await conn.execute(text(sql))
                logger.info("✓ OK")
            except Exception as e:
                logger.warning(f"⚠ {e}")

    logger.info("\n✅ Миграция завершена!")
    logger.info("Все ENUM теперь используют значения в нижнем регистре")


if __name__ == "__main__":
    print("=== Миграция ENUM значений ===\n")
    asyncio.run(fix_enum_values())
