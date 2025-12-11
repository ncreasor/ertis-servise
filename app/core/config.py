"""
Конфигурация приложения
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения"""

    # Application
    APP_NAME: str = Field(default="Ertis Service", description="Название приложения")
    APP_VERSION: str = Field(default="1.0.0", description="Версия приложения")
    DEBUG: bool = Field(default=False, description="Режим отладки")
    ENVIRONMENT: str = Field(default="production", description="Окружение")

    # Server
    HOST: str = Field(default="0.0.0.0", description="Хост сервера")
    PORT: int = Field(default=8000, description="Порт сервера")

    # CORS
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Разрешенные origins для CORS"
    )

    # Security
    SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="Секретный ключ для JWT"
    )
    ALGORITHM: str = Field(default="HS256", description="Алгоритм шифрования")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Время жизни access token в минутах"
    )

    # Database
    DATABASE_URL: str = Field(
        default="mysql+aiomysql://user:password@localhost:3306/ertis_db",
        description="URL подключения к базе данных"
    )

    # OpenAI
    OPENAI_API_KEY: str = Field(
        default="",
        description="API ключ OpenAI"
    )

    # File Storage
    UPLOAD_DIR: str = Field(default="uploads", description="Директория для загрузки файлов")
    MAX_FILE_SIZE: int = Field(default=10485760, description="Максимальный размер файла (10MB)")

    # Yandex Maps API
    YANDEX_MAPS_API_KEY: str = Field(
        default="",
        description="API ключ Яндекс.Карт"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")

    @property
    def allowed_origins_list(self) -> List[str]:
        """Возвращает список разрешенных origins"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        """Конфигурация Pydantic"""
        env_file = ".env"
        case_sensitive = True


# Создаем глобальный экземпляр настроек
settings = Settings()
