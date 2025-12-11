"""
Модель сотрудника ЖКХ
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Employee(BaseModel):
    """Модель сотрудника ЖКХ"""
    __tablename__ = "employees"

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    photo_url = Column(String(500), nullable=True)
    average_rating = Column(Float, default=0.0)

    # Foreign Keys
    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("housing_organizations.id"), nullable=False)

    # Relationships
    specialty = relationship("Specialty", back_populates="employees")
    organization = relationship("HousingOrganization", back_populates="employees")
    assigned_requests = relationship("Request", back_populates="assignee", foreign_keys="Request.assignee_id")
    ratings = relationship("Rating", back_populates="employee")
