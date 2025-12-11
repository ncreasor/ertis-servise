"""
Pydantic схемы для оценки
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RatingBase(BaseModel):
    """Базовая схема оценки"""
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: Optional[str] = Field(None, max_length=1000)


class RatingCreate(RatingBase):
    """Схема для создания оценки"""
    pass  # request_id передается через URL path параметр


class RatingResponse(RatingBase):
    """Схема ответа с оценкой"""
    id: int
    request_id: int
    user_id: int
    employee_id: int
    created_at: datetime

    class Config:
        from_attributes = True
