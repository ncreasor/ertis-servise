"""
Настройка логирования приложения
"""
import sys
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """
    Настройка логирования для приложения
    """
    # Удаляем стандартный обработчик
    logger.remove()

    # Добавляем кастомный обработчик с форматированием
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=settings.LOG_LEVEL,
    )

    # Добавляем обработчик для записи в файл
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.LOG_LEVEL,
    )

    logger.info("Логирование настроено")


def get_logger():
    """Получить экземпляр логгера"""
    return logger
