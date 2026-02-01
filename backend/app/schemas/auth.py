"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """Registration request schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str | None = None


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request schema."""

    refresh_token: str


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: str
    type: str
    exp: int
    iat: int
