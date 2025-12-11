"""
Pydantic схемы для смены пароля
"""
from pydantic import BaseModel, Field


class PasswordChange(BaseModel):
    """Схема для смены пароля"""
    old_password: str = Field(..., min_length=6, max_length=100, description="Текущий пароль")
    new_password: str = Field(..., min_length=6, max_length=100, description="Новый пароль")
