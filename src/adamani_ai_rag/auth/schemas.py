"""User schemas for API requests/responses."""
from typing import Optional
import uuid

from fastapi_users import schemas
from pydantic import field_validator


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for reading user data."""
    full_name: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""
    full_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """Validate password length (bcrypt has a 72 byte limit)."""
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password must be 72 bytes or less')
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data."""
    full_name: Optional[str] = None
