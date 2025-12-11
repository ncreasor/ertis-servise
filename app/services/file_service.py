"""
Сервис для работы с файлами
"""
import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from PIL import Image
from io import BytesIO

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
MAX_IMAGE_SIZE = (2048, 2048)  # Максимальный размер изображения


def allowed_file(filename: str) -> bool:
    """Проверка допустимого расширения файла"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


async def save_upload_file(upload_file: UploadFile, subfolder: str = "general") -> str:
    """
    Сохранение загруженного файла

    Args:
        upload_file: Загруженный файл
        subfolder: Подпапка для сохранения (requests, employees, solutions)

    Returns:
        Относительный путь к сохраненному файлу
    """
    try:
        # Проверка размера файла
        content = await upload_file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Размер файла превышает максимально допустимый ({settings.MAX_FILE_SIZE} байт)"
            )

        # Проверка расширения
        if not allowed_file(upload_file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Генерация уникального имени файла
        file_extension = upload_file.filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Создание директории если не существует
        upload_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, unique_filename)

        # Оптимизация изображения
        try:
            image = Image.open(BytesIO(content))

            # Изменение размера если изображение слишком большое
            if image.size[0] > MAX_IMAGE_SIZE[0] or image.size[1] > MAX_IMAGE_SIZE[1]:
                image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                logger.info(f"Изображение изменено до {image.size}")

            # Конвертация в RGB если необходимо
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Сохранение оптимизированного изображения
            image.save(file_path, quality=85, optimize=True)

        except Exception as e:
            logger.warning(f"Не удалось оптимизировать изображение: {e}, сохраняем как есть")
            # Сохранение оригинального файла
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

        # Возвращаем относительный путь
        relative_path = os.path.join(subfolder, unique_filename)
        logger.info(f"Файл сохранен: {relative_path}")

        return relative_path

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")
    finally:
        await upload_file.seek(0)  # Сбрасываем позицию чтения файла


async def delete_file(file_path: str) -> bool:
    """
    Удаление файла

    Args:
        file_path: Относительный путь к файлу

    Returns:
        True если файл успешно удален
    """
    try:
        full_path = os.path.join(settings.UPLOAD_DIR, file_path)

        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"Файл удален: {file_path}")
            return True
        else:
            logger.warning(f"Файл не найден: {file_path}")
            return False

    except Exception as e:
        logger.error(f"Ошибка при удалении файла: {e}")
        return False


def get_file_url(file_path: str) -> str:
    """
    Получение URL файла

    Args:
        file_path: Относительный путь к файлу

    Returns:
        URL файла
    """
    if file_path:
        return f"/uploads/{file_path}"
    return None
