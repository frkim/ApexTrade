"""User schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str
    full_name: str | None = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: str | None = None
    username: str | None = Field(None, min_length=3, max_length=50)


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    """Password change request schema."""

    current_password: str
    new_password: str = Field(..., min_length=8)
