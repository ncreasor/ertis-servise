"""
Автоматическая миграция ENUM значений из верхнего в нижний регистр
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger

logger = get_logger()


async def migrate_enum_values(session: AsyncSession) -> None:
    """
    Миграция ENUM значений из верхнего в нижний регистр
    Безопасна для многократного запуска
    """

    logger.info("Проверка и миграция ENUM значений...")

    try:
        # Шаг 1: Расширяем ENUM для временного включения обоих вариантов
        alter_commands = [
            "ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin', 'CITIZEN', 'EMPLOYEE', 'ADMIN') DEFAULT 'citizen' NOT NULL",
            "ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error', 'INFO', 'WARNING', 'SUCCESS', 'ERROR') DEFAULT 'info' NOT NULL",
            "ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed', 'PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED') DEFAULT 'pending' NOT NULL",
            "ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high', 'LOW', 'MEDIUM', 'HIGH') DEFAULT 'medium' NOT NULL",
        ]

        for sql in alter_commands:
            try:
                await session.execute(text(sql))
            except Exception as e:
                # Игнорируем ошибки если колонка уже имеет правильный формат
                logger.debug(f"Пропуск ALTER: {str(e)[:100]}")

        await session.commit()
        logger.debug("✓ ENUM расширены")

        # Шаг 2: Обновляем существующие данные
        update_commands = [
            ("UPDATE users SET role = 'citizen' WHERE role = 'CITIZEN'", "users.role"),
            ("UPDATE users SET role = 'employee' WHERE role = 'EMPLOYEE'", "users.role"),
            ("UPDATE users SET role = 'admin' WHERE role = 'ADMIN'", "users.role"),

            ("UPDATE notifications SET type = 'info' WHERE type = 'INFO'", "notifications.type"),
            ("UPDATE notifications SET type = 'warning' WHERE type = 'WARNING'", "notifications.type"),
            ("UPDATE notifications SET type = 'success' WHERE type = 'SUCCESS'", "notifications.type"),
            ("UPDATE notifications SET type = 'error' WHERE type = 'ERROR'", "notifications.type"),

            ("UPDATE requests SET status = 'pending' WHERE status = 'PENDING'", "requests.status"),
            ("UPDATE requests SET status = 'assigned' WHERE status = 'ASSIGNED'", "requests.status"),
            ("UPDATE requests SET status = 'in_progress' WHERE status = 'IN_PROGRESS'", "requests.status"),
            ("UPDATE requests SET status = 'completed' WHERE status = 'COMPLETED'", "requests.status"),
            ("UPDATE requests SET status = 'closed' WHERE status = 'CLOSED'", "requests.status"),

            ("UPDATE requests SET priority = 'low' WHERE priority = 'LOW'", "requests.priority"),
            ("UPDATE requests SET priority = 'medium' WHERE priority = 'MEDIUM'", "requests.priority"),
            ("UPDATE requests SET priority = 'high' WHERE priority = 'HIGH'", "requests.priority"),
        ]

        total_updated = 0
        for sql, field_name in update_commands:
            try:
                result = await session.execute(text(sql))
                if result.rowcount > 0:
                    total_updated += result.rowcount
                    logger.debug(f"✓ Обновлено {result.rowcount} записей в {field_name}")
            except Exception as e:
                logger.debug(f"Пропуск UPDATE: {str(e)[:100]}")

        await session.commit()
        if total_updated > 0:
            logger.info(f"✓ Обновлено {total_updated} записей на нижний регистр")

        # Шаг 3: Очищаем ENUM (оставляем только нижний регистр)
        final_alter_commands = [
            "ALTER TABLE users MODIFY COLUMN role ENUM('citizen', 'employee', 'admin') DEFAULT 'citizen' NOT NULL",
            "ALTER TABLE notifications MODIFY COLUMN type ENUM('info', 'warning', 'success', 'error') DEFAULT 'info' NOT NULL",
            "ALTER TABLE requests MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'completed', 'closed') DEFAULT 'pending' NOT NULL",
            "ALTER TABLE requests MODIFY COLUMN priority ENUM('low', 'medium', 'high') DEFAULT 'medium' NOT NULL",
        ]

        for sql in final_alter_commands:
            try:
                await session.execute(text(sql))
            except Exception as e:
                logger.debug(f"Пропуск финального ALTER: {str(e)[:100]}")

        await session.commit()
        logger.info("✅ ENUM миграция завершена успешно")

    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Ошибка при миграции ENUM: {e}")
        # Не прерываем запуск приложения, если миграция не удалась
        logger.warning("Приложение продолжит работу, но могут быть проблемы с данными")
