"""Authentication and Session Management service."""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.core.security import hash_password, verify_password, create_access_token
from backend.core.exceptions import UnauthorizedException, ConflictException, BadRequestException
from backend.models.user import User
from backend.models.audit import AuditLog
from backend.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, payload: UserRegisterRequest, ip_address: Optional[str] = None) -> User:
        """Register a new user with secure password hashing and initial settings."""
        existing = self.db.query(User).filter(User.email == payload.email.lower()).first()
        if existing:
            raise ConflictException(f"Account with email '{payload.email}' already exists.")
        
        user = User(
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            preferred_currency=payload.preferred_currency.upper(),
            is_active=True,
            is_verified=True, # default for standalone setup
        )
        self.db.add(user)
        self.db.flush()

        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="register",
            status="success",
            ip_address=ip_address,
            details={"email": user.email, "currency": user.preferred_currency}
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, payload: UserLoginRequest, ip_address: Optional[str] = None) -> TokenResponse:
        """Authenticate user credentials and return a signed JWT token."""
        user = self.db.query(User).filter(User.email == payload.email.lower()).first()
        if not user or not verify_password(payload.password, user.hashed_password):
            if user:
                audit = AuditLog(
                    user_id=user.id,
                    action="login_failure",
                    status="denied",
                    ip_address=ip_address,
                    details={"reason": "invalid_password"}
                )
                self.db.add(audit)
                self.db.commit()
            raise UnauthorizedException("Incorrect email or password.")
        
        if not user.is_active:
            raise UnauthorizedException("Account is disabled.")
        
        # Audit successful login
        audit = AuditLog(
            user_id=user.id,
            action="login",
            status="success",
            ip_address=ip_address,
            details={"email": user.email}
        )
        self.db.add(audit)
        self.db.commit()

        token_data = {
            "sub": user.id,
            "user_id": user.id,
            "email": user.email,
        }
        token = create_access_token(token_data)

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in_minutes=1440,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            preferred_currency=user.preferred_currency
        )
