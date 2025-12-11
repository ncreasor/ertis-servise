"""
Pydantic схемы для чата
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    """Сообщение в чате"""
    role: str = Field(..., description="Роль отправителя (user/assistant)")
    content: str = Field(..., description="Содержимое сообщения")


class ChatRequest(BaseModel):
    """Запрос к чат-боту"""
    message: str = Field(..., min_length=1, max_length=1000, description="Сообщение пользователя")
    history: Optional[List[ChatMessage]] = Field(default=None, description="История чата")


class ChatResponse(BaseModel):
    """Ответ чат-бота"""
    message: str = Field(..., description="Ответ ассистента")
    timestamp: str = Field(..., description="Временная метка")
