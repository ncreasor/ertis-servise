"""
Модель категории проблемы
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Category(BaseModel):
    """Модель категории проблемы (сфера)"""
    __tablename__ = "categories"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Relationships
    requests = relationship("Request", back_populates="category")
    specialties = relationship("Specialty", back_populates="category")
