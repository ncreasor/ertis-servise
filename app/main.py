"""
Главный модуль FastAPI приложения
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.v1.router import api_router

# Настройка логирования
setup_logging()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    # Startup
    logger.info(f"Запуск приложения {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Окружение: {settings.ENVIRONMENT}")
    logger.info(f"Debug режим: {settings.DEBUG}")

    # Создаем директорию для логов если её нет
    os.makedirs("logs", exist_ok=True)

    # Создаем директорию для загрузки файлов
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Инициализация базы данных
    from app.core.database import init_db, AsyncSessionLocal
    try:
        await init_db()
        logger.info("База данных инициализирована")

        # Добавление начальных данных
        from app.services.init_data import init_categories_and_specialties, create_demo_data
        async with AsyncSessionLocal() as session:
            try:
                await init_categories_and_specialties(session)
                # Раскомментируйте следующую строку для создания демо-данных
                # await create_demo_data(session)
            except Exception as e:
                logger.error(f"Ошибка при инициализации данных: {e}")

    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")

    yield

    # Shutdown
    logger.info("Завершение работы приложения")


# Создание приложения FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API сервис Ertis",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Корневой эндпоинт
@app.get(
    "/",
    tags=["Root"],
    summary="Корневой эндпоинт",
    description="Возвращает информацию о сервисе"
)
async def root():
    """Корневой эндпоинт"""
    return JSONResponse(
        content={
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/api/docs",
            "redoc": "/api/redoc"
        }
    )


# Подключение роутеров
app.include_router(api_router, prefix="/api/v1")

# Раздача статических файлов (загруженные изображения)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик исключений"""
    logger.error(f"Необработанное исключение: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "Внутренняя ошибка сервера"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
