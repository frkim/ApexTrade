"""User profile endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import PasswordChange, UserResponse, UserUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    current_user: CurrentUser,
) -> User:
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    request: UserUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> User:
    """Update current user profile."""
    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.flush()
    await db.refresh(current_user)

    logger.info(f"User profile updated: {current_user.email}")
    return current_user


@router.post("/me/change-password")
async def change_password(
    request: PasswordChange,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """Change current user password."""
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.hashed_password = get_password_hash(request.new_password)
    await db.flush()

    logger.info(f"Password changed for user: {current_user.email}")
    return {"message": "Password changed successfully"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete current user account."""
    await db.delete(current_user)
    logger.info(f"User account deleted: {current_user.email}")
