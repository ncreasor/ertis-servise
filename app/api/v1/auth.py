"""
API эндпоинты для аутентификации
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.schemas.user import UserCreate, UserResponse
from app.schemas.employee import EmployeeLogin
from app.schemas.auth import Token
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя"""

    # Проверка уникальности username
    result = await db.execute(select(User).where(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует"
        )

    # Проверка уникальности email если указан
    if user_data.email:
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_email = result.scalar_one_or_none()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

    # Создание пользователя
    password_hash = get_password_hash(user_data.password)

    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        role=UserRole.USER
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"Зарегистрирован новый пользователь: {new_user.username}")

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Универсальный вход для пользователей, сотрудников и админов ЖКХ"""

    # Сначала ищем среди пользователей
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if user and verify_password(form_data.password, user.password_hash):
        # Пользователь найден и пароль верный
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role.value
            }
        )

        logger.info(f"Успешный вход пользователя: {user.username}")

        return {"access_token": access_token, "token_type": "bearer"}

    # Если не найден среди пользователей, ищем среди сотрудников
    result = await db.execute(select(Employee).where(Employee.username == form_data.username))
    employee = result.scalar_one_or_none()

    if employee and verify_password(form_data.password, employee.password_hash):
        # Сотрудник найден и пароль верный
        access_token = create_access_token(
            data={
                "sub": employee.username,
                "user_id": -1,  # У сотрудников нет user_id
                "role": UserRole.EMPLOYEE.value,
                "employee_id": employee.id
            }
        )

        logger.info(f"Успешный вход сотрудника: {employee.username}")

        return {"access_token": access_token, "token_type": "bearer"}

    # Неверные учетные данные
    logger.warning(f"Неудачная попытка входа: {form_data.username}")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный username или пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Получение информации о текущем пользователе"""
    return current_user


from app.core.dependencies import get_current_active_user
