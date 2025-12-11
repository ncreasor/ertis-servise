"""
Модель оценки работы сотрудника
"""
from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Rating(BaseModel):
    """Модель оценки работы сотрудника"""
    __tablename__ = "ratings"

    rating = Column(Integer, nullable=False)  # Оценка от 1 до 5
    comment = Column(Text, nullable=True)

    # Foreign Keys
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    # Relationships
    request = relationship("Request", back_populates="ratings")
    user = relationship("User", back_populates="ratings")
    employee = relationship("Employee", back_populates="ratings")
