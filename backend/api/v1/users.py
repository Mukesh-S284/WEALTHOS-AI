"""User settings, profile management, data export, and deletion routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.services.user_service import UserService
from backend.schemas.user import UserProfileResponse, UserUpdateRequest, PasswordChangeRequest
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/users", tags=["Users & Preferences"])


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Retrieve full user profile and preferences."""
    return current_user


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences (currency, locale, timezone, theme, income, risk tolerance)."""
    service = UserService(db)
    updated = service.update_profile(current_user, payload)
    return updated


@router.post("/change-password")
def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Secure password change with validation of existing password."""
    service = UserService(db)
    service.change_password(current_user, payload)
    return {"message": "Password changed successfully."}


@router.get("/export-data")
def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data in structured JSON format."""
    service = UserService(db)
    return service.export_user_data(current_user)


@router.delete("/account")
def delete_user_account(
    confirmation: str = Query(..., description="Must explicitly be 'DELETE_MY_ACCOUNT'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently delete user account and all cascaded data."""
    service = UserService(db)
    service.delete_user_account(current_user, confirmation)
    return {"message": "User account and all associated records permanently deleted."}
