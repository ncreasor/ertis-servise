"""
Модель специальности сотрудника
"""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Specialty(BaseModel):
    """Модель специальности (род деятельности)"""
    __tablename__ = "specialties"

    name = Column(String(100), nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="specialties")
    employees = relationship("Employee", back_populates="specialty")
