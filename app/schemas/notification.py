"""
Pydantic схемы для уведомлений
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.notification import NotificationType


class NotificationBase(BaseModel):
    """Базовая схема уведомления"""
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: NotificationType = Field(default=NotificationType.INFO)


class NotificationCreate(NotificationBase):
    """Схема для создания уведомления"""
    user_id: int


class NotificationResponse(NotificationBase):
    """Схема ответа с уведомлением"""
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
