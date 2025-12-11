"""
Pydantic схемы для сотрудника
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    """Базовая схема сотрудника"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    specialty_id: int
    organization_id: int


class EmployeeCreate(EmployeeBase):
    """Схема для создания сотрудника"""
    password: str = Field(..., min_length=6, max_length=100)
    photo_url: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """Схема ответа с сотрудником"""
    id: int
    photo_url: Optional[str] = None
    average_rating: float
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeUpdate(BaseModel):
    """Схема для обновления сотрудника"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    specialty_id: Optional[int] = None
    photo_url: Optional[str] = None


class EmployeeLogin(BaseModel):
    """Схема для входа сотрудника"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
