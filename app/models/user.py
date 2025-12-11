"""
Модель пользователя
"""
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """Роли пользователей"""
    CITIZEN = "citizen"
    EMPLOYEE = "employee"
    ADMIN = "admin"


class User(BaseModel):
    """Модель пользователя"""
    __tablename__ = "users"

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CITIZEN, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    requests = relationship("Request", back_populates="creator", foreign_keys="Request.creator_id")
    ratings = relationship("Rating", back_populates="user")
