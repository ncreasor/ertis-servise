"""
API эндпоинты для работы с уведомлениями
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter()


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех уведомлений текущего пользователя"""

    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    notifications = result.scalars().all()

    return notifications


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Пометить уведомление как прочитанное"""

    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )

    # Проверка что уведомление принадлежит текущему пользователю
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете изменить это уведомление"
        )

    notification.is_read = True

    await db.commit()
    await db.refresh(notification)

    logger.info(f"Уведомление {notification_id} помечено как прочитанное")

    return {"message": "Уведомление помечено как прочитанное"}
