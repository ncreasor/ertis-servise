"""
API эндпоинты для работы с адресами (автокомплит)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()

router = APIRouter()


@router.get("/suggest")
async def suggest_addresses(
    query: str = Query(..., min_length=3, description="Поисковый запрос адреса")
) -> Dict[str, Any]:
    """
    Автокомплит адресов через Яндекс.Карты API

    Возвращает список подходящих адресов на основе введенного текста
    """

    if not settings.YANDEX_MAPS_API_KEY:
        logger.warning("YANDEX_MAPS_API_KEY не установлен")
        raise HTTPException(
            status_code=503,
            detail="Сервис автокомплита адресов временно недоступен"
        )

    try:
        # Используем Yandex Geocoder API
        url = "https://geocode-maps.yandex.ru/1.x/"

        params = {
            "apikey": settings.YANDEX_MAPS_API_KEY,
            "geocode": query,
            "format": "json",
            "results": 3,
            "lang": "ru_RU"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        # Парсим результаты
        suggestions = []

        geo_objects = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])

        for item in geo_objects:
            geo_object = item.get("GeoObject", {})

            # Получаем адрес
            address = geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {}).get("text", "")

            # Получаем координаты
            pos = geo_object.get("Point", {}).get("pos", "")
            coords = pos.split() if pos else []

            if address:
                suggestion = {
                    "address": address,
                    "coordinates": {
                        "latitude": float(coords[1]) if len(coords) > 1 else None,
                        "longitude": float(coords[0]) if len(coords) > 0 else None
                    } if coords else None
                }
                suggestions.append(suggestion)

        logger.info(f"Найдено {len(suggestions)} адресов для запроса: {query}")

        return {
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions)
        }

    except httpx.HTTPError as e:
        logger.error(f"Ошибка при запросе к Yandex API: {e}")
        raise HTTPException(
            status_code=503,
            detail="Ошибка при получении данных от сервиса геокодирования"
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка в suggest_addresses: {e}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/geocode")
async def geocode_address(
    address: str = Query(..., min_length=5, description="Полный адрес для геокодирования")
) -> Dict[str, Any]:
    """
    Получение координат по адресу
    """

    if not settings.YANDEX_MAPS_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Сервис геокодирования временно недоступен"
        )

    try:
        url = "https://geocode-maps.yandex.ru/1.x/"

        params = {
            "apikey": settings.YANDEX_MAPS_API_KEY,
            "geocode": address,
            "format": "json",
            "results": 1,
            "lang": "ru_RU"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        geo_objects = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])

        if not geo_objects:
            raise HTTPException(
                status_code=404,
                detail="Адрес не найден"
            )

        geo_object = geo_objects[0].get("GeoObject", {})

        # Получаем координаты
        pos = geo_object.get("Point", {}).get("pos", "")
        coords = pos.split() if pos else []

        # Получаем точный адрес
        full_address = geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {}).get("text", "")

        return {
            "address": full_address,
            "coordinates": {
                "latitude": float(coords[1]) if len(coords) > 1 else None,
                "longitude": float(coords[0]) if len(coords) > 0 else None
            } if coords else None
        }

    except HTTPException:
        raise
    except httpx.HTTPError as e:
        logger.error(f"Ошибка при запросе к Yandex API: {e}")
        raise HTTPException(
            status_code=503,
            detail="Ошибка при получении данных от сервиса геокодирования"
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка в geocode_address: {e}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера"
        )
