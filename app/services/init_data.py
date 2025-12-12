"""
Инициализация начальных данных в БД
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.category import Category
from app.models.specialty import Specialty
from app.core.logging import get_logger

logger = get_logger()


async def init_categories_and_specialties(db: AsyncSession):
    """Создание начальных категорий и специальностей"""

    # Проверяем существуют ли уже категории
    result = await db.execute(select(Category))
    existing_categories = result.scalars().all()

    if existing_categories:
        logger.info("Категории уже существуют, пропускаем инициализацию")
        return

    # Данные категорий и связанных специальностей
    categories_data = [
        {
            "name": "Водоснабжение",
            "description": "Проблемы с водопроводом, канализацией, горячей и холодной водой",
            "specialties": ["Сантехник", "Слесарь-сантехник"]
        },
        {
            "name": "Электричество",
            "description": "Проблемы с электропроводкой, освещением, электрощитовыми",
            "specialties": ["Электрик", "Электромонтер"]
        },
        {
            "name": "Дорожное покрытие",
            "description": "Ямы на дорогах, трещины асфальта, проблемы с тротуарами",
            "specialties": ["Дорожный рабочий", "Асфальтоукладчик"]
        },
        {
            "name": "Вывоз мусора",
            "description": "Переполненные контейнеры, несвоевременный вывоз мусора",
            "specialties": ["Дворник", "Мусорщик"]
        },
        {
            "name": "Уборка территории",
            "description": "Уборка снега, листьев, мусора во дворе и подъезде",
            "specialties": ["Дворник", "Уборщик территории"]
        },
        {
            "name": "Лифт",
            "description": "Неисправности лифта, застревание, шум",
            "specialties": ["Лифтер", "Механик лифтового оборудования"]
        },
        {
            "name": "Благоустройство",
            "description": "Озеленение, детские площадки, скамейки, освещение двора",
            "specialties": ["Рабочий по благоустройству", "Озеленитель", "Плотник"]
        },
        {
            "name": "Отопление",
            "description": "Проблемы с отоплением, батареями, теплоснабжением",
            "specialties": ["Слесарь-сантехник", "Теплотехник"]
        },
        {
            "name": "Подъезд",
            "description": "Освещение в подъезде, замки, домофон, почтовые ящики",
            "specialties": ["Электрик", "Слесарь", "Дворник"]
        }
    ]

    # Создаем категории и специальности
    for category_data in categories_data:
        # Создаем категорию
        category = Category(
            name=category_data["name"],
            description=category_data["description"]
        )
        db.add(category)
        await db.flush()  # Чтобы получить ID категории

        # Создаем специальности для категории
        for specialty_name in category_data["specialties"]:
            # Проверяем существует ли уже такая специальность
            result = await db.execute(
                select(Specialty).where(Specialty.name == specialty_name)
            )
            existing_specialty = result.scalar_one_or_none()

            if not existing_specialty:
                specialty = Specialty(
                    name=specialty_name,
                    category_id=category.id
                )
                db.add(specialty)

        logger.info(f"Создана категория: {category.name}")

    await db.commit()
    logger.info("Начальные данные (категории и специальности) успешно добавлены")


async def create_demo_data(db: AsyncSession):
    """Создание демо-данных для тестирования (опционально)"""

    from app.models.housing_organization import HousingOrganization
    from app.models.user import User, UserRole
    from app.models.employee import Employee
    from app.core.security import get_password_hash

    # Проверяем есть ли уже демо-организация
    result = await db.execute(
        select(HousingOrganization).where(HousingOrganization.name == "Демо ЖКХ")
    )
    existing_org = result.scalar_one_or_none()

    if existing_org:
        logger.info("Демо-данные уже существуют")
        return

    # Создаем демо организацию ЖКХ
    demo_org = HousingOrganization(
        name="Демо ЖКХ",
        description="Демонстрационная организация для тестирования",
        phone="+7 (7182) 32-00-01",
        email="demo@ertis.kz",
        address="г. Павлодар, ул. Ленина, д. 1"
    )
    db.add(demo_org)
    await db.flush()

    # Создаем демо админа ЖКХ
    demo_admin = User(
        first_name="Админ",
        last_name="ЖКХ",
        username="admin",
        email="admin@ertis.kz",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    db.add(demo_admin)

    # Создаем демо пользователя (жильца)
    demo_user = User(
        first_name="Иван",
        last_name="Иванов",
        username="user",
        email="user@example.com",
        password_hash=get_password_hash("user123"),
        role=UserRole.CITIZEN
    )
    db.add(demo_user)

    # Создаем демо сотрудника (рабочего)
    demo_worker_user = User(
        first_name="Алексей",
        last_name="Петров",
        username="worker",
        email="worker@ertis.kz",
        password_hash=get_password_hash("worker123"),
        role=UserRole.EMPLOYEE
    )
    db.add(demo_worker_user)
    await db.flush()

    # Получаем специальность "Электрик"
    specialty_result = await db.execute(
        select(Specialty).where(Specialty.name == "Электрик")
    )
    specialty = specialty_result.scalar_one_or_none()

    if specialty:
        # Создаем запись сотрудника
        demo_employee = Employee(
            first_name="Алексей",
            last_name="Петров",
            user_id=demo_worker_user.id,
            specialty_id=specialty.id,
            organization_id=demo_org.id,
            phone="+7 (777) 123-45-67",
            average_rating=4.5
        )
        db.add(demo_employee)

    await db.commit()

    logger.info("Демо-данные созданы:")
    logger.info("  Админ ЖКХ - username: admin, password: admin123")
    logger.info("  Житель - username: user, password: user123")
    logger.info("  Рабочий - username: worker, password: worker123")
