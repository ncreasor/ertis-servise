"""
Pydantic схемы для аутентификации
"""
from pydantic import BaseModel, Field
from typing import Optional

from app.models.user import UserRole


class Token(BaseModel):
    """Схема токена"""
    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Схема ответа при аутентификации"""
    access_token: str
    token_type: str = "bearer"
    user: dict  # User object будет добавлен динамически


class TokenData(BaseModel):
    """Данные токена"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    employee_id: Optional[int] = None  # Если это сотрудник
