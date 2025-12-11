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
    category_id: int


class RequestCreate(RequestBase):
    """Схема для создания заявки"""
    pass


class RequestResponse(RequestBase):
    """Схема ответа с заявкой"""
    id: int
    photo_url: Optional[str] = None
    solution_photo_url: Optional[str] = None
    status: RequestStatus
    priority: int
    creator_id: int
    assignee_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RequestUpdate(BaseModel):
    """Схема для обновления заявки"""
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    category_id: Optional[int] = None
    status: Optional[RequestStatus] = None
    priority: Optional[int] = None


class RequestAssign(BaseModel):
    """Схема для назначения заявки сотруднику"""
    assignee_id: int


class RequestComplete(BaseModel):
    """Схема для завершения заявки"""
    status: RequestStatus = Field(default=RequestStatus.COMPLETED)


class RequestClose(BaseModel):
    """Схема для закрытия заявки пользователем"""
    status: RequestStatus = Field(..., description="Статус: completed или spam")
