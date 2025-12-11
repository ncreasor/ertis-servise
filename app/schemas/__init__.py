"""
Pydantic схемы
"""
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.schemas.auth import Token, TokenData
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.specialty import SpecialtyCreate, SpecialtyResponse
from app.schemas.housing_organization import (
    HousingOrganizationCreate,
    HousingOrganizationResponse,
    HousingOrganizationUpdate,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    EmployeeLogin,
)
from app.schemas.request import (
    RequestCreate,
    RequestResponse,
    RequestUpdate,
    RequestAssign,
    RequestComplete,
    RequestClose,
)
from app.schemas.rating import RatingCreate, RatingResponse

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "Token",
    "TokenData",
    "CategoryCreate",
    "CategoryResponse",
    "CategoryUpdate",
    "SpecialtyCreate",
    "SpecialtyResponse",
    "HousingOrganizationCreate",
    "HousingOrganizationResponse",
    "HousingOrganizationUpdate",
    "EmployeeCreate",
    "EmployeeResponse",
    "EmployeeUpdate",
    "EmployeeLogin",
    "RequestCreate",
    "RequestResponse",
    "RequestUpdate",
    "RequestAssign",
    "RequestComplete",
    "RequestClose",
    "RatingCreate",
    "RatingResponse",
]
