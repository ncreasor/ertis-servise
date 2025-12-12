"""
Сервис для отправки уведомлений пользователям
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationType
from app.core.logging import get_logger

logger = get_logger()


async def send_notification(
    db: AsyncSession,
    user_id: int,
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.INFO
) -> Notification:
    """
    Отправить уведомление пользователю
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type
    )
    
    db.add(notification)
    await db.flush()
    
    logger.info(f"Уведомление отправлено пользователю {user_id}: {title}")
    
    return notification


async def notify_request_assigned(db: AsyncSession, user_id: int, request_id: int, employee_name: str):
    """Уведомить о назначении заявки"""
    await send_notification(
        db=db,
        user_id=user_id,
        title="Заявка назначена",
        message=f"Ваша заявка #{request_id} назначена на сотрудника {employee_name}. Скоро проблема будет решена!",
        notification_type=NotificationType.INFO
    )


async def notify_request_in_progress(db: AsyncSession, user_id: int, request_id: int):
    """Уведомить о начале работы над заявкой"""
    await send_notification(
        db=db,
        user_id=user_id,
        title="Работа начата",
        message=f"Сотрудник начал работу над вашей заявкой #{request_id}.",
        notification_type=NotificationType.INFO
    )


async def notify_request_completed(db: AsyncSession, user_id: int, request_id: int):
    """Уведомить о завершении заявки"""
    await send_notification(
        db=db,
        user_id=user_id,
        title="Заявка выполнена! ✅",
        message=f"Ваша заявка #{request_id} успешно выполнена. Пожалуйста, оцените работу сотрудника.",
        notification_type=NotificationType.SUCCESS
    )


async def notify_request_closed(db: AsyncSession, user_id: int, request_id: int, reason: str = None):
    """Уведомить о закрытии заявки"""
    message = f"Ваша заявка #{request_id} была закрыта."
    if reason:
        message += f" Причина: {reason}"
    
    await send_notification(
        db=db,
        user_id=user_id,
        title="Заявка закрыта",
        message=message,
        notification_type=NotificationType.INFO
    )


async def notify_status_changed(db: AsyncSession, user_id: int, request_id: int, new_status: str):
    """Уведомить об изменении статуса заявки"""
    status_labels = {
        'pending': 'ожидает',
        'assigned': 'назначена',
        'in_progress': 'в работе',
        'completed': 'выполнена',
        'closed': 'закрыта'
    }
    
    status_label = status_labels.get(new_status, new_status)
    
    await send_notification(
        db=db,
        user_id=user_id,
        title="Статус заявки изменён",
        message=f"Статус вашей заявки #{request_id} изменён на: {status_label}",
        notification_type=NotificationType.INFO
    )


async def notify_employee_assigned_task(db: AsyncSession, employee_user_id: int, request_id: int, address: str):
    """Уведомить сотрудника о новой задаче"""
    await send_notification(
        db=db,
        user_id=employee_user_id,
        title="Новая задача! 📋",
        message=f"Вам назначена заявка #{request_id}. Адрес: {address}",
        notification_type=NotificationType.INFO
    )

