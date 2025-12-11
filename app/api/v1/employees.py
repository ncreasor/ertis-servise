"""
API эндпоинты для работы с сотрудниками
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.core.database import get_db
from app.core.dependencies import require_role, get_current_employee
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.models.specialty import Specialty
from app.models.housing_organization import HousingOrganization
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.file_service import save_upload_file
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter()


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Создание нового сотрудника (для админов ЖКХ)"""

    # Проверка уникальности username
    result = await db.execute(select(Employee).where(Employee.username == employee_data.username))
    existing_employee = result.scalar_one_or_none()

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сотрудник с таким username уже существует"
        )

    # Проверка существования специальности
    result = await db.execute(select(Specialty).where(Specialty.id == employee_data.specialty_id))
    specialty = result.scalar_one_or_none()

    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Специальность не найдена"
        )

    # Проверка существования организации
    result = await db.execute(
        select(HousingOrganization).where(HousingOrganization.id == employee_data.organization_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация ЖКХ не найдена"
        )

    # Хеширование пароля
    password_hash = get_password_hash(employee_data.password)

    # Создание сотрудника
    new_employee = Employee(
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        username=employee_data.username,
        password_hash=password_hash,
        photo_url=employee_data.photo_url,
        specialty_id=employee_data.specialty_id,
        organization_id=employee_data.organization_id,
        average_rating=0.0
    )

    db.add(new_employee)
    await db.commit()
    await db.refresh(new_employee)

    logger.info(f"Создан новый сотрудник: {new_employee.username}")

    return new_employee


@router.get("", response_model=List[EmployeeResponse])
async def get_employees(
    organization_id: int = None,
    specialty_id: int = None,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка сотрудников (для админов ЖКХ)"""

    query = select(Employee)

    if organization_id:
        query = query.where(Employee.organization_id == organization_id)
    if specialty_id:
        query = query.where(Employee.specialty_id == specialty_id)

    query = query.order_by(Employee.average_rating.desc())

    result = await db.execute(query)
    employees = result.scalars().all()

    return employees


@router.get("/me", response_model=EmployeeResponse)
async def get_current_employee_info(
    current_employee: Employee = Depends(get_current_employee),
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о текущем сотруднике"""
    return current_employee


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о конкретном сотруднике"""

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )

    return employee


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Обновление информации о сотруднике (для админов ЖКХ)"""

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )

    # Обновление полей
    if employee_data.first_name is not None:
        employee.first_name = employee_data.first_name
    if employee_data.last_name is not None:
        employee.last_name = employee_data.last_name
    if employee_data.specialty_id is not None:
        # Проверка существования специальности
        result = await db.execute(select(Specialty).where(Specialty.id == employee_data.specialty_id))
        specialty = result.scalar_one_or_none()
        if not specialty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Специальность не найдена"
            )
        employee.specialty_id = employee_data.specialty_id
    if employee_data.photo_url is not None:
        employee.photo_url = employee_data.photo_url

    await db.commit()
    await db.refresh(employee)

    logger.info(f"Обновлена информация о сотруднике {employee_id}")

    return employee


@router.post("/{employee_id}/upload-photo", response_model=EmployeeResponse)
async def upload_employee_photo(
    employee_id: int,
    photo: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Загрузка фото сотрудника"""

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )

    # Сохранение фото
    photo_path = await save_upload_file(photo, subfolder="employees")
    employee.photo_url = photo_path

    await db.commit()
    await db.refresh(employee)

    logger.info(f"Загружено фото для сотрудника {employee_id}")

    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Удаление сотрудника (для админов ЖКХ)"""

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )

    await db.delete(employee)
    await db.commit()

    logger.info(f"Удален сотрудник {employee_id}")

    return None
