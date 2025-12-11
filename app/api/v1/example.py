"""
Пример API роутера с CRUD операциями
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel, Field

router = APIRouter()


# Временное хранилище (в реальном приложении используйте БД)
items_storage = {}
item_id_counter = 1


class ItemCreate(BaseModel):
    """Схема для создания элемента"""
    name: str = Field(..., min_length=1, max_length=100, description="Название")
    description: str = Field(..., max_length=500, description="Описание")


class ItemUpdate(BaseModel):
    """Схема для обновления элемента"""
    name: str = Field(None, min_length=1, max_length=100, description="Название")
    description: str = Field(None, max_length=500, description="Описание")


class ItemResponse(BaseModel):
    """Схема ответа с элементом"""
    id: int = Field(..., description="ID элемента")
    name: str = Field(..., description="Название")
    description: str = Field(..., description="Описание")


@router.get(
    "/items",
    response_model=List[ItemResponse],
    tags=["Items"],
    summary="Получить список всех элементов",
    description="Возвращает список всех созданных элементов"
)
async def get_items() -> List[ItemResponse]:
    """Получить все элементы"""
    return list(items_storage.values())


@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    tags=["Items"],
    summary="Получить элемент по ID",
    description="Возвращает элемент по указанному ID"
)
async def get_item(item_id: int) -> ItemResponse:
    """Получить элемент по ID"""
    if item_id not in items_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Элемент с ID {item_id} не найден"
        )
    return items_storage[item_id]


@router.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Items"],
    summary="Создать новый элемент",
    description="Создает новый элемент и возвращает его данные"
)
async def create_item(item: ItemCreate) -> ItemResponse:
    """Создать новый элемент"""
    global item_id_counter

    new_item = ItemResponse(
        id=item_id_counter,
        name=item.name,
        description=item.description
    )
    items_storage[item_id_counter] = new_item
    item_id_counter += 1

    return new_item


@router.put(
    "/items/{item_id}",
    response_model=ItemResponse,
    tags=["Items"],
    summary="Обновить элемент",
    description="Обновляет существующий элемент"
)
async def update_item(item_id: int, item: ItemUpdate) -> ItemResponse:
    """Обновить элемент"""
    if item_id not in items_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Элемент с ID {item_id} не найден"
        )

    stored_item = items_storage[item_id]
    update_data = item.model_dump(exclude_unset=True)

    updated_item = stored_item.model_copy(update=update_data)
    items_storage[item_id] = updated_item

    return updated_item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Items"],
    summary="Удалить элемент",
    description="Удаляет элемент по ID"
)
async def delete_item(item_id: int):
    """Удалить элемент"""
    if item_id not in items_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Элемент с ID {item_id} не найден"
        )

    del items_storage[item_id]
    return None
