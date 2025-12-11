"""
Pydantic схемы для организации ЖКХ
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class HousingOrganizationBase(BaseModel):
    """Базовая схема организации ЖКХ"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)


class HousingOrganizationCreate(HousingOrganizationBase):
    """Схема для создания организации ЖКХ"""
    pass


class HousingOrganizationResponse(HousingOrganizationBase):
    """Схема ответа с организацией ЖКХ"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class HousingOrganizationUpdate(BaseModel):
    """Схема для обновления организации ЖКХ"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
