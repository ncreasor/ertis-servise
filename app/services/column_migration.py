"""
Автоматическая миграция: добавление новых колонок в существующие таблицы
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger

logger = get_logger()


async def migrate_add_columns(session: AsyncSession) -> None:
    """
    Добавляет новые колонки в таблицу requests если их нет.
    Безопасна для многократного запуска.
    """
    
    logger.info("Проверка и добавление новых колонок...")
    
    # Колонки которые нужно добавить
    columns_to_add = [
        {
            "table": "requests",
            "column": "ai_analysis",
            "definition": "TEXT NULL",
            "after": "ai_category"
        },
        {
            "table": "requests", 
            "column": "ai_recommendation",
            "definition": "TEXT NULL",
            "after": "ai_analysis"
        }
    ]
    
    for col_info in columns_to_add:
        table = col_info["table"]
        column = col_info["column"]
        definition = col_info["definition"]
        after = col_info.get("after", "")
        
        try:
            # Проверяем существует ли колонка
            check_sql = text(f"""
                SELECT COUNT(*) as cnt 
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                AND column_name = '{column}'
            """)
            result = await session.execute(check_sql)
            row = result.fetchone()
            
            if row and row[0] == 0:
                # Колонка не существует - добавляем
                after_clause = f"AFTER {after}" if after else ""
                alter_sql = text(f"ALTER TABLE {table} ADD COLUMN {column} {definition} {after_clause}")
                await session.execute(alter_sql)
                await session.commit()
                logger.info(f"✓ Добавлена колонка {table}.{column}")
            else:
                logger.debug(f"Колонка {table}.{column} уже существует")
                
        except Exception as e:
            await session.rollback()
            logger.warning(f"Пропуск добавления {table}.{column}: {str(e)[:100]}")
    
    logger.info("✅ Миграция колонок завершена")

