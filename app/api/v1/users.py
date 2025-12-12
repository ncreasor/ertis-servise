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
    current_user: User = Depends(require_role([UserRole.ADMIN])),
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


@router.get("", response_model=list[UserResponse])
async def get_all_users(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка всех пользователей (для админов)"""
    
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    
    return users


@router.post("/setup-test-accounts", response_model=MessageResponse)
async def setup_test_accounts(
    db: AsyncSession = Depends(get_db)
):
    """
    Создание тестовых аккаунтов (публичный эндпоинт для первоначальной настройки).
    Пароль для всех: 123456
    """
    
    test_accounts = [
        {"first_name": "Админ", "last_name": "ЖКХ", "username": "admin", "email": "admin@ertis.kz", "role": UserRole.ADMIN},
        {"first_name": "Менеджер", "last_name": "Системы", "username": "manager", "email": "manager@ertis.kz", "role": UserRole.ADMIN},
        {"first_name": "Иван", "last_name": "Иванов", "username": "user", "email": "user@example.com", "role": UserRole.CITIZEN},
        {"first_name": "Алексей", "last_name": "Петров", "username": "worker", "email": "worker@ertis.kz", "role": UserRole.EMPLOYEE},
    ]
    
    created = []
    password_hash = get_password_hash("123456")
    
    for account in test_accounts:
        # Проверяем существует ли
        result = await db.execute(select(User).where(User.username == account["username"]))
        existing = result.scalar_one_or_none()
        
        if existing:
            # Обновляем пароль
            existing.password_hash = password_hash
            created.append(f"{account['username']} (обновлен)")
        else:
            # Создаём нового
            new_user = User(
                first_name=account["first_name"],
                last_name=account["last_name"],
                username=account["username"],
                email=account["email"],
                password_hash=password_hash,
                role=account["role"]
            )
            db.add(new_user)
            created.append(account["username"])
    
    await db.commit()
    
    logger.info(f"Созданы/обновлены тестовые аккаунты: {created}")
    
    return MessageResponse(
        message=f"Тестовые аккаунты готовы: {', '.join(created)}. Пароль для всех: 123456"
    )


@router.patch("/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Изменение роли пользователя (для админов)"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    old_role = user.role
    user.role = new_role
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"Админ {current_user.username} изменил роль пользователя {user.username}: {old_role} -> {new_role}")
    
    return user
