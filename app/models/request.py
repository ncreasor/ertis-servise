"""
Модель заявки
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class RequestStatus(str, enum.Enum):
    """Статусы заявки"""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SPAM = "spam"
    CANCELLED = "cancelled"


class RequestPriority(int, enum.Enum):
    """Приоритет заявки (1-5, где 5 - самый высокий)"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class Request(BaseModel):
    """Модель заявки на решение проблемы"""
    __tablename__ = "requests"

    # Основная информация
    description = Column(Text, nullable=False)
    address = Column(String(500), nullable=False)
    photo_url = Column(String(500), nullable=True)  # Фото проблемы
    solution_photo_url = Column(String(500), nullable=True)  # Фото решения

    # Статус и приоритет
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.NEW, nullable=False)
    priority = Column(Integer, default=RequestPriority.MEDIUM.value, nullable=False)

    # Даты
    completed_at = Column(DateTime, nullable=True)

    # Foreign Keys
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    # Relationships
    category = relationship("Category", back_populates="requests")
    creator = relationship("User", back_populates="requests", foreign_keys=[creator_id])
    assignee = relationship("Employee", back_populates="assigned_requests", foreign_keys=[assignee_id])
    ratings = relationship("Rating", back_populates="request", uselist=False)
