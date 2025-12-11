"""
API эндпоинты для статистики
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.models.request import Request, RequestStatus
from app.models.employee import Employee
from app.models.rating import Rating
from app.models.category import Category
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter()


@router.get("/overview")
async def get_statistics_overview(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Общая статистика (для админов ЖКХ)"""

    # Общее количество заявок
    total_requests = await db.execute(select(func.count(Request.id)))
    total_requests_count = total_requests.scalar()

    # Количество заявок по статусам
    status_counts = {}
    for status in RequestStatus:
        count = await db.execute(
            select(func.count(Request.id)).where(Request.status == status)
        )
        status_counts[status.value] = count.scalar()

    # Количество заявок за последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_requests = await db.execute(
        select(func.count(Request.id)).where(Request.created_at >= thirty_days_ago)
    )
    recent_requests_count = recent_requests.scalar()

    # Средний рейтинг всех сотрудников
    avg_employee_rating = await db.execute(
        select(func.avg(Employee.average_rating))
    )
    avg_rating = avg_employee_rating.scalar() or 0.0

    # Количество сотрудников
    total_employees = await db.execute(select(func.count(Employee.id)))
    total_employees_count = total_employees.scalar()

    # Среднее время выполнения заявки (в часах)
    completed_requests = await db.execute(
        select(Request).where(
            and_(
                Request.status == RequestStatus.COMPLETED,
                Request.completed_at.isnot(None)
            )
        )
    )
    completed_list = completed_requests.scalars().all()

    avg_completion_time = 0.0
    if completed_list:
        total_time = sum([
            (req.completed_at - req.created_at).total_seconds() / 3600
            for req in completed_list
        ])
        avg_completion_time = total_time / len(completed_list)

    # Распределение заявок по категориям
    categories_result = await db.execute(
        select(Category.name, func.count(Request.id))
        .join(Request, Request.category_id == Category.id)
        .group_by(Category.name)
    )
    categories_stats = {name: count for name, count in categories_result.all()}

    # Топ-5 лучших сотрудников по рейтингу
    top_employees = await db.execute(
        select(Employee)
        .order_by(Employee.average_rating.desc())
        .limit(5)
    )
    top_employees_list = [
        {
            "id": emp.id,
            "name": f"{emp.first_name} {emp.last_name}",
            "rating": emp.average_rating
        }
        for emp in top_employees.scalars().all()
    ]

    return {
        "total_requests": total_requests_count,
        "recent_requests_30_days": recent_requests_count,
        "status_distribution": status_counts,
        "total_employees": total_employees_count,
        "average_employee_rating": round(float(avg_rating), 2),
        "average_completion_time_hours": round(avg_completion_time, 2),
        "requests_by_category": categories_stats,
        "top_employees": top_employees_list
    }


@router.get("/employee/{employee_id}")
async def get_employee_statistics(
    employee_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Статистика по конкретному сотруднику"""

    # Проверка существования сотрудника
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        return {"error": "Сотрудник не найден"}

    # Общее количество заявок
    total_requests = await db.execute(
        select(func.count(Request.id)).where(Request.assignee_id == employee_id)
    )
    total_count = total_requests.scalar()

    # Завершенные заявки
    completed_requests = await db.execute(
        select(func.count(Request.id)).where(
            and_(
                Request.assignee_id == employee_id,
                Request.status == RequestStatus.COMPLETED
            )
        )
    )
    completed_count = completed_requests.scalar()

    # Текущие активные заявки
    active_requests = await db.execute(
        select(func.count(Request.id)).where(
            and_(
                Request.assignee_id == employee_id,
                Request.status.in_([RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS])
            )
        )
    )
    active_count = active_requests.scalar()

    # Все оценки сотрудника
    ratings_result = await db.execute(
        select(Rating).where(Rating.employee_id == employee_id)
    )
    ratings_list = ratings_result.scalars().all()

    # Распределение оценок
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in ratings_list:
        rating_distribution[rating.rating] += 1

    return {
        "employee_id": employee_id,
        "name": f"{employee.first_name} {employee.last_name}",
        "average_rating": employee.average_rating,
        "total_requests": total_count,
        "completed_requests": completed_count,
        "active_requests": active_count,
        "completion_rate": round((completed_count / total_count * 100) if total_count > 0 else 0, 2),
        "rating_distribution": rating_distribution,
        "total_ratings": len(ratings_list)
    }


@router.get("/requests/priority")
async def get_requests_by_priority(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Распределение заявок по приоритетам"""

    priority_stats = {}
    for priority in range(1, 6):
        count = await db.execute(
            select(func.count(Request.id)).where(Request.priority == priority)
        )
        priority_stats[f"priority_{priority}"] = count.scalar()

    return priority_stats
