"""Authentication API routes."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.services.auth_service import AuthService
from backend.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from backend.schemas.user import UserProfileResponse
from backend.api.deps import get_current_user, rate_limit
from backend.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(limit_per_minute=10))]
)
def register(
    payload: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user account."""
    ip = request.client.host if request.client else None
    service = AuthService(db)
    user = service.register_user(payload, ip_address=ip)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit(limit_per_minute=20))]
)
def login(
    payload: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Log in and retrieve a signed JWT token."""
    ip = request.client.host if request.client else None
    service = AuthService(db)
    token_response = service.authenticate_user(payload, ip_address=ip)
    return token_response


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Retrieve authenticated user's profile."""
    return current_user


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
):
    """Session logout endpoint."""
    return {"message": "Successfully logged out. Please discard your client token."}
