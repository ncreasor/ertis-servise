#!/bin/bash

# Скрипт запуска Ertis Service для macOS
# Автоматически создает и активирует виртуальное окружение

set -e  # Останавливаем выполнение при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Ertis Service Launcher ===${NC}"

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 не найден. Пожалуйста, установите Python 3.8+${NC}"
    exit 1
fi

# Проверяем версию Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}Найден Python версии: ${PYTHON_VERSION}${NC}"

# Переходим в директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Создаем виртуальное окружение, если его нет
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Виртуальное окружение не найдено. Создаем...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}Виртуальное окружение создано${NC}"
fi

# Активируем виртуальное окружение
echo -e "${GREEN}Активируем виртуальное окружение...${NC}"
source venv/bin/activate

# Обновляем pip
echo -e "${GREEN}Обновляем pip...${NC}"
pip install --upgrade pip --quiet

# Устанавливаем зависимости
echo -e "${GREEN}Проверяем зависимости...${NC}"
pip install -r requirements.txt --quiet

# Создаем .env файл, если его нет
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}.env файл не найден. Копируем из .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env файл создан. Не забудьте настроить параметры!${NC}"
fi

# Создаем необходимые директории
mkdir -p logs
mkdir -p uploads

# Проверяем наличие .env настроек
if grep -q "your-secret-key-here-change-in-production" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  ВНИМАНИЕ: Не забудьте настроить .env файл:${NC}"
    echo -e "${YELLOW}   - DATABASE_URL (MySQL)${NC}"
    echo -e "${YELLOW}   - OPENAI_API_KEY${NC}"
    echo -e "${YELLOW}   - YANDEX_MAPS_API_KEY${NC}"
    echo -e "${YELLOW}   - SECRET_KEY${NC}"
    echo ""
fi

# Запускаем приложение
echo -e "${GREEN}=== Запускаем сервер ===${NC}"
echo -e "${GREEN}📚 Документация: http://localhost:8000/api/docs${NC}"
echo -e "${GREEN}🔍 ReDoc: http://localhost:8000/api/redoc${NC}"
echo ""
python run.py
