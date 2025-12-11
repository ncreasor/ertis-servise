"""
Dependencies для FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data: TokenData = decode_access_token(token)

    if token_data is None or token_data.user_id is None:
        raise credentials_exception

    # Получаем пользователя из БД
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Получение активного пользователя"""
    return current_user


def require_role(required_roles: list[UserRole]):
    """Проверка роли пользователя"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции"
            )
        return current_user
    return role_checker


async def get_current_employee(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Employee:
    """Получение текущего сотрудника из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data: TokenData = decode_access_token(token)

    if token_data is None or token_data.employee_id is None:
        raise credentials_exception

    # Получаем сотрудника из БД
    result = await db.execute(select(Employee).where(Employee.id == token_data.employee_id))
    employee = result.scalar_one_or_none()

    if employee is None:
        raise credentials_exception

    return employee
