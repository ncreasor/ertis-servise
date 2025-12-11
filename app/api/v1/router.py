"""
Главный роутер для API v1
"""
from fastapi import APIRouter
from app.api.v1 import (
    health,
    auth,
    requests,
    employees,
    categories,
    statistics,
    addresses
)

# Создаем главный роутер для v1
api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(requests.router, prefix="/requests", tags=["Requests"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["Addresses"])
