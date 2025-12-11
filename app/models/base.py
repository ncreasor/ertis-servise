"""
Базовая модель для всех моделей БД
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class BaseModel(Base):
    """Базовая модель с общими полями"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
