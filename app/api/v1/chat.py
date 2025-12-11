"""
API эндпоинты для чата с AI ассистентом
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import get_chat_response
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(chat_request: ChatRequest):
    """
    Отправить сообщение AI ассистенту
    """
    try:
        # Получаем ответ от AI
        response_message = await get_chat_response(
            user_message=chat_request.message,
            history=chat_request.history
        )

        logger.info(f"Чат: получено сообщение '{chat_request.message[:50]}...'")

        return ChatResponse(
            message=response_message,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Ошибка в чате: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке сообщения"
        )
