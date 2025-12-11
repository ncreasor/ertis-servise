"""
Модель заявки
"""
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class RequestStatus(str, enum.Enum):
    """Статусы заявки"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


class RequestPriority(str, enum.Enum):
    """Приоритет заявки"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Request(BaseModel):
    """Модель заявки на решение проблемы"""
    __tablename__ = "requests"

    # Основная информация
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    problem_type = Column(String(100), nullable=True)
    address = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    photo_url = Column(String(500), nullable=True)  # Фото проблемы
    completion_photo_url = Column(String(500), nullable=True)  # Фото решения (renamed from solution_photo_url)
    completion_note = Column(Text, nullable=True)  # Заметка при завершении

    # AI Analysis
    ai_category = Column(String(100), nullable=True)
    ai_description = Column(Text, nullable=True)

    # Статус и приоритет
    status = Column(SQLEnum(RequestStatus, values_callable=lambda x: [e.value for e in x]), default=RequestStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(RequestPriority, values_callable=lambda x: [e.value for e in x]), default=RequestPriority.MEDIUM, nullable=False)

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
