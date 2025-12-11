"""
Pydantic схемы для пользователя
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

from app.models.user import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Схема для входа"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class UserResponse(UserBase):
    """Схема ответа с пользователем"""
    id: int
    role: UserRole
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
