"""User schemas for API requests/responses."""
from typing import Optional
import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for reading user data."""
    full_name: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""
    full_name: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data."""
    full_name: Optional[str] = None
