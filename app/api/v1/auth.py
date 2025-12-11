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
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.employee import EmployeeLogin
from app.schemas.auth import Token, AuthResponse
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
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

    # Проверка уникальности email
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_email = result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    # Проверка уникальности phone
    result = await db.execute(select(User).where(User.phone == user_data.phone))
    existing_phone = result.scalar_one_or_none()

    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким телефоном уже существует"
        )

    # Создание пользователя
    password_hash = get_password_hash(user_data.password)

    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        middle_name=user_data.middle_name,
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=password_hash,
        role=UserRole.CITIZEN
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"Зарегистрирован новый пользователь: {new_user.username}")

    # Создаем токен
    access_token = create_access_token(
        data={
            "sub": new_user.username,
            "user_id": new_user.id,
            "role": new_user.role.value
        }
    )

    # Формируем user объект для ответа
    user_dict = UserResponse.model_validate(new_user).model_dump()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Универсальный вход для пользователей, сотрудников и админов ЖКХ"""

    # Ищем пользователя по email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if user and verify_password(login_data.password, user.password_hash):
        # Пользователь найден и пароль верный
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role.value
            }
        )

        logger.info(f"Успешный вход пользователя: {user.username}")

        # Формируем user объект для ответа
        user_dict = UserResponse.model_validate(user).model_dump()

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_dict
        }

    # Если не найден или пароль неверный
    # Также проверяем среди сотрудников (они могут входить через username в отдельном эндпоинте)
    logger.warning(f"Неудачная попытка входа: {login_data.email}")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный email или пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )
