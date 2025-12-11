"""
Pydantic схемы для специальности
"""
from pydantic import BaseModel, Field
from datetime import datetime


class SpecialtyBase(BaseModel):
    """Базовая схема специальности"""
    name: str = Field(..., min_length=1, max_length=100)
    category_id: int


class SpecialtyCreate(SpecialtyBase):
    """Схема для создания специальности"""
    pass


class SpecialtyResponse(SpecialtyBase):
    """Схема ответа с специальностью"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
