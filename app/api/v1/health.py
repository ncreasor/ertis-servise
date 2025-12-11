"""
Health check эндпоинт
"""
from fastapi import APIRouter
from datetime import datetime
from app.schemas.base import HealthCheck
from app.core.config import settings

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheck,
    tags=["Health"],
    summary="Проверка работоспособности сервиса",
    description="Возвращает статус сервиса и его версию"
)
async def health_check() -> HealthCheck:
    """
    Проверка здоровья сервиса

    Returns:
        HealthCheck: Информация о статусе сервиса
    """
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
    )
