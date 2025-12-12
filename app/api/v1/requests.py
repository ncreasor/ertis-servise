"""
API эндпоинты для работы с заявками
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_role, get_current_employee
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.models.request import Request, RequestStatus, RequestPriority
from app.models.category import Category
from app.models.rating import Rating
from app.schemas.request import (
    RequestCreate,
    RequestResponse,
    RequestUpdate,
    RequestAssign,
    RequestComplete,
    RequestClose
)
from app.schemas.rating import RatingCreate, RatingResponse
from app.services.file_service import save_upload_file, get_file_url
from app.services.openai_service import (
    analyze_problem_description,
    analyze_image_priority,
    assign_employee_ai,
    generate_user_recommendation
)
from app.core.logging import get_logger
from app.core.config import settings
import os

logger = get_logger()

router = APIRouter()


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    description: str = Form(...),
    address: str = Form(...),
    category: str = Form(...),
    problem_type: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    photo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Создание новой заявки (для пользователей)"""

    # Ищем категорию по имени
    result = await db.execute(select(Category).where(Category.name == category))
    category_obj = result.scalar_one_or_none()

    if not category_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категория '{category}' не найдена"
        )

    # Сохранение фото если есть
    photo_path = None
    if photo:
        photo_path = await save_upload_file(photo, subfolder="requests")

    # Создание заявки
    new_request = Request(
        description=description,
        address=address,
        problem_type=problem_type,
        latitude=latitude,
        longitude=longitude,
        category_id=category_obj.id,
        creator_id=current_user.id,
        photo_url=photo_path,
        status=RequestStatus.PENDING,
        priority=RequestPriority.MEDIUM  # По умолчанию средний приоритет
    )

    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)

    # Асинхронная обработка через OpenAI (только если есть фото)
    if photo_path:
        try:
            # 1. Анализируем описание проблемы (внутренний анализ)
            structured_description = await analyze_problem_description(
                description=description,
                category_name=category_obj.name
            )

            # Сохраняем AI анализ (внутреннее поле, не показывается пользователю напрямую)
            new_request.ai_analysis = structured_description
            new_request.ai_category = category_obj.name

            # 2. Анализируем фото и определяем приоритет
            full_photo_path = os.path.join(settings.UPLOAD_DIR, photo_path)
            priority_str = await analyze_image_priority(
                image_path=full_photo_path,
                structured_description=structured_description,
                category_name=category_obj.name
            )

            # Обновляем приоритет заявки (преобразуем строку в enum)
            priority_mapping = {
                "low": RequestPriority.LOW,
                "medium": RequestPriority.MEDIUM,
                "high": RequestPriority.HIGH
            }
            new_request.priority = priority_mapping.get(priority_str.lower(), RequestPriority.MEDIUM)
            
            # 3. Генерируем рекомендацию для пользователя
            user_recommendation = await generate_user_recommendation(
                description=description,
                category_name=category_obj.name,
                priority=priority_str.lower()
            )
            new_request.ai_recommendation = user_recommendation

            # 3. Автоматическое назначение на сотрудника
            # Получаем доступных сотрудников для этой категории
            from app.models.specialty import Specialty

            result = await db.execute(
                select(Employee)
                .join(Specialty)
                .where(Specialty.category_id == category_obj.id)
            )
            available_employees = result.scalars().all()

            if available_employees:
                # Подготавливаем данные о сотрудниках
                employees_data = []
                for emp in available_employees:
                    # Считаем активные заявки сотрудника
                    active_count = await db.execute(
                        select(func.count(Request.id))
                        .where(
                            and_(
                                Request.assignee_id == emp.id,
                                Request.status.in_([RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS])
                            )
                        )
                    )
                    active_requests = active_count.scalar()

                    employees_data.append({
                        "id": emp.id,
                        "name": f"{emp.first_name} {emp.last_name}",
                        "specialty": emp.specialty.name,
                        "rating": emp.average_rating,
                        "active_requests": active_requests
                    })

                # Используем AI для выбора сотрудника
                selected_employee_id = await assign_employee_ai(
                    request_description=description,
                    category_name=category_obj.name,
                    priority=new_request.priority.value,
                    available_employees=employees_data
                )

                if selected_employee_id:
                    new_request.assignee_id = selected_employee_id
                    new_request.status = RequestStatus.ASSIGNED
                    logger.info(f"Заявка {new_request.id} автоматически назначена на сотрудника {selected_employee_id}")

            await db.commit()
            await db.refresh(new_request)

        except Exception as e:
            logger.error(f"Ошибка при обработке заявки через AI: {e}")
            # Заявка уже создана, просто логируем ошибку
            await db.commit()
            await db.refresh(new_request)

    logger.info(f"Создана заявка #{new_request.id} от пользователя {current_user.username}")

    return new_request


@router.get("/map", response_model=List[RequestResponse])
async def get_requests_for_map(
    db: AsyncSession = Depends(get_db)
):
    """
    Получение заявок для отображения на карте (публичный endpoint).
    Возвращает только заявки с координатами и статусами: pending, assigned, in_progress
    """
    result = await db.execute(
        select(Request)
        .where(
            and_(
                Request.latitude.isnot(None),
                Request.longitude.isnot(None),
                Request.status.in_([
                    RequestStatus.PENDING,
                    RequestStatus.ASSIGNED,
                    RequestStatus.IN_PROGRESS
                ])
            )
        )
        .order_by(Request.created_at.desc())
        .limit(100)
    )
    requests = result.scalars().all()
    return requests


@router.get("/my", response_model=List[RequestResponse])
async def get_my_requests(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение своих заявок (для пользователей)"""

    result = await db.execute(
        select(Request)
        .where(Request.creator_id == current_user.id)
        .order_by(Request.created_at.desc())
    )
    requests = result.scalars().all()

    return requests


@router.get("/assigned", response_model=List[RequestResponse])
async def get_assigned_requests(
    current_employee: Employee = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db)
):
    """Получение назначенных заявок (для сотрудников)"""

    result = await db.execute(
        select(Request)
        .where(Request.assignee_id == current_employee.id)
        .order_by(Request.priority.desc(), Request.created_at.asc())
    )
    requests = result.scalars().all()

    return requests


@router.get("", response_model=List[RequestResponse])
async def get_all_requests(
    status_filter: Optional[RequestStatus] = None,
    category_id: Optional[int] = None,
    priority: Optional[int] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех заявок с фильтрами (для админов ЖКХ)"""

    query = select(Request)

    # Применяем фильтры
    if status_filter:
        query = query.where(Request.status == status_filter)
    if category_id:
        query = query.where(Request.category_id == category_id)
    if priority:
        query = query.where(Request.priority == priority)

    query = query.order_by(Request.priority.desc(), Request.created_at.desc())

    result = await db.execute(query)
    requests = result.scalars().all()

    return requests


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение конкретной заявки"""

    result = await db.execute(select(Request).where(Request.id == request_id))
    request_obj = result.scalar_one_or_none()

    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    # Проверка прав доступа
    if current_user.role == UserRole.USER and request_obj.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой заявке"
        )

    return request_obj


@router.patch("/{request_id}/assign", response_model=RequestResponse)
async def assign_request(
    request_id: int,
    assign_data: RequestAssign,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Назначение заявки на сотрудника (для админов ЖКХ)"""

    result = await db.execute(select(Request).where(Request.id == request_id))
    request_obj = result.scalar_one_or_none()

    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    # Проверка существования сотрудника
    result = await db.execute(select(Employee).where(Employee.id == assign_data.assignee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )

    request_obj.assignee_id = assign_data.assignee_id
    request_obj.status = RequestStatus.ASSIGNED

    await db.commit()
    await db.refresh(request_obj)

    logger.info(f"Заявка #{request_id} назначена на сотрудника {assign_data.assignee_id}")

    return request_obj


@router.patch("/{request_id}/complete", response_model=RequestResponse)
async def complete_request(
    request_id: int,
    completion_photo: Optional[UploadFile] = File(None),
    completion_note: Optional[str] = Form(None),
    current_employee: Employee = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db)
):
    """Завершение заявки с фото решения (для сотрудников)"""

    result = await db.execute(select(Request).where(Request.id == request_id))
    request_obj = result.scalar_one_or_none()

    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    # Проверка что заявка назначена на этого сотрудника
    if request_obj.assignee_id != current_employee.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Эта заявка не назначена на вас"
        )

    # Сохранение фото решения если есть
    if completion_photo:
        completion_photo_path = await save_upload_file(completion_photo, subfolder="solutions")
        request_obj.completion_photo_url = completion_photo_path

    # Сохранение заметки если есть
    if completion_note:
        request_obj.completion_note = completion_note

    request_obj.status = RequestStatus.COMPLETED
    request_obj.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(request_obj)

    logger.info(f"Заявка #{request_id} завершена сотрудником {current_employee.id}")

    return request_obj


@router.patch("/{request_id}/close", response_model=RequestResponse)
async def close_request(
    request_id: int,
    reason: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Закрытие заявки (для пользователей)"""

    result = await db.execute(select(Request).where(Request.id == request_id))
    request_obj = result.scalar_one_or_none()

    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    # Проверка что это заявка пользователя
    if request_obj.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете закрывать только свои заявки"
        )

    # Закрываем заявку
    request_obj.status = RequestStatus.CLOSED

    # Сохраняем причину в completion_note если указана
    if reason:
        request_obj.completion_note = reason

    if not request_obj.completed_at:
        request_obj.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(request_obj)

    logger.info(f"Заявка #{request_id} закрыта пользователем")

    return request_obj


@router.post("/{request_id}/rate", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def rate_request(
    request_id: int,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Оценка работы сотрудника по завершенной заявке"""

    result = await db.execute(select(Request).where(Request.id == request_id))
    request_obj = result.scalar_one_or_none()

    if not request_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )

    # Проверка что это заявка пользователя
    if request_obj.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете оценивать только свои заявки"
        )

    # Проверка что заявка завершена
    if request_obj.status != RequestStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно оценивать только завершенные заявки"
        )

    # Проверка что заявка была назначена на сотрудника
    if not request_obj.assignee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заявка не была назначена на сотрудника"
        )

    # Проверка что оценка еще не поставлена
    result = await db.execute(select(Rating).where(Rating.request_id == request_id))
    existing_rating = result.scalar_one_or_none()

    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Оценка уже была поставлена для этой заявки"
        )

    # Создание оценки
    new_rating = Rating(
        rating=rating_data.rating,
        comment=rating_data.comment,
        request_id=request_id,
        user_id=current_user.id,
        employee_id=request_obj.assignee_id
    )

    db.add(new_rating)

    # Пересчет средней оценки сотрудника
    result = await db.execute(
        select(func.avg(Rating.rating))
        .where(Rating.employee_id == request_obj.assignee_id)
    )
    avg_rating = result.scalar()

    employee_result = await db.execute(
        select(Employee).where(Employee.id == request_obj.assignee_id)
    )
    employee = employee_result.scalar_one()
    employee.average_rating = float(avg_rating) if avg_rating else 0.0

    await db.commit()
    await db.refresh(new_rating)

    logger.info(f"Поставлена оценка {rating_data.rating} для заявки #{request_id}")

    return new_rating
