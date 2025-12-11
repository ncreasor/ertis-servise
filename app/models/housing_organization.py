"""
Модель организации ЖКХ
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class HousingOrganization(BaseModel):
    """Модель организации ЖКХ"""
    __tablename__ = "housing_organizations"

    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)

    # Relationships
    employees = relationship("Employee", back_populates="organization")
