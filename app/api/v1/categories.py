"""
API эндпоинты для работы с категориями
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Получение списка всех категорий (доступно всем)"""

    result = await db.execute(select(Category).order_by(Category.name))
    categories = result.scalars().all()

    return categories


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Создание новой категории (для админов ЖКХ)"""

    # Проверка уникальности названия
    result = await db.execute(select(Category).where(Category.name == category_data.name))
    existing_category = result.scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким названием уже существует"
        )

    new_category = Category(
        name=category_data.name,
        description=category_data.description
    )

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    logger.info(f"Создана новая категория: {new_category.name}")

    return new_category


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение конкретной категории"""

    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )

    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Обновление категории (для админов ЖКХ)"""

    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )

    if category_data.name is not None:
        category.name = category_data.name
    if category_data.description is not None:
        category.description = category_data.description

    await db.commit()
    await db.refresh(category)

    logger.info(f"Обновлена категория {category_id}")

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Удаление категории (для админов ЖКХ)"""

    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )

    await db.delete(category)
    await db.commit()

    logger.info(f"Удалена категория {category_id}")

    return None
