"""
Pydantic схемы для заявки
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.request import RequestStatus, RequestPriority


class RequestBase(BaseModel):
    """Базовая схема заявки"""
    description: str = Field(..., min_length=10, max_length=2000)
    address: str = Field(..., min_length=5, max_length=500)


class RequestCreate(RequestBase):
    """Схема для создания заявки"""
    pass


class RequestResponse(BaseModel):
    """Схема ответа с заявкой"""
    id: int
    user_id: int = Field(validation_alias='creator_id')  # Совместимость с фронтом (creator_id)
    category_id: Optional[int] = None
    title: Optional[str] = None
    description: str
    problem_type: Optional[str] = None
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None
    completion_photo_url: Optional[str] = None
    completion_note: Optional[str] = None
    status: RequestStatus
    priority: RequestPriority
    assigned_employee_id: Optional[int] = Field(None, validation_alias='assignee_id')  # Совместимость с фронтом
    ai_category: Optional[str] = None
    ai_recommendation: Optional[str] = None  # Рекомендация AI для пользователя
    ai_analysis: Optional[str] = None  # Внутренний AI анализ
    ai_description: Optional[str] = None  # Legacy
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class RequestUpdate(BaseModel):
    """Схема для обновления заявки"""
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    category_id: Optional[int] = None
    status: Optional[RequestStatus] = None
    priority: Optional[int] = None


class RequestAssign(BaseModel):
    """Схема для назначения заявки сотруднику"""
    assignee_id: int = Field(..., validation_alias="employee_id")

    class Config:
        populate_by_name = True  # Разрешает использовать оба имени: assignee_id и employee_id


class RequestComplete(BaseModel):
    """Схема для завершения заявки"""
    status: RequestStatus = Field(default=RequestStatus.COMPLETED)


class RequestClose(BaseModel):
    """Схема для закрытия заявки пользователем"""
    status: RequestStatus = Field(..., description="Статус: completed или spam")
