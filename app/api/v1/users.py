"""
API эндпоинты для работы с пользователями
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_role
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.password import PasswordChange
from app.schemas.base import MessageResponse
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Получение своего профиля"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление своего профиля"""

    # Проверка уникальности email если меняется
    if user_data.email and user_data.email != current_user.email:
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_email = result.scalar_one_or_none()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

    # Обновление полей
    if user_data.first_name is not None:
        current_user.first_name = user_data.first_name
    if user_data.last_name is not None:
        current_user.last_name = user_data.last_name
    if user_data.email is not None:
        current_user.email = user_data.email

    await db.commit()
    await db.refresh(current_user)

    logger.info(f"Пользователь {current_user.username} обновил свой профиль")

    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.HOUSING_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Получение профиля пользователя по ID (для админов)"""

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    return user


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Изменение пароля"""

    # Проверка текущего пароля
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль"
        )

    # Установка нового пароля
    current_user.password_hash = get_password_hash(password_data.new_password)

    await db.commit()

    logger.info(f"Пользователь {current_user.username} сменил пароль")

    return MessageResponse(message="Пароль успешно изменен")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Удаление своего аккаунта"""

    await db.delete(current_user)
    await db.commit()

    logger.info(f"Пользователь {current_user.username} удалил свой аккаунт")

    return None
