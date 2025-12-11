"""
Pydantic схемы для категории
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """Базовая схема категории"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Схема для создания категории"""
    pass


class CategoryResponse(CategoryBase):
    """Схема ответа с категорией"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    """Схема для обновления категории"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
