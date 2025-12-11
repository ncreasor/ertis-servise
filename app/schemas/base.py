"""
Базовые схемы для API
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class HealthCheck(BaseModel):
    """Схема для health check"""
    status: str = Field(..., description="Статус сервиса")
    version: str = Field(..., description="Версия приложения")
    timestamp: datetime = Field(..., description="Временная метка")


class MessageResponse(BaseModel):
    """Схема для простого ответа с сообщением"""
    message: str = Field(..., description="Сообщение")
    data: Optional[Any] = Field(None, description="Дополнительные данные")


class ErrorResponse(BaseModel):
    """Схема для ошибок"""
    error: str = Field(..., description="Тип ошибки")
    message: str = Field(..., description="Описание ошибки")
    details: Optional[Any] = Field(None, description="Детали ошибки")
