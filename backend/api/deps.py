"""FastAPI route dependencies: database session, authentication, and authorization."""

from typing import Generator, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import decode_access_token
from backend.core.exceptions import UnauthorizedException, ForbiddenException
from backend.models.user import User

security_scheme = HTTPBearer(auto_error=False)

# In-memory rate limiting tracker: IP/Key -> list of timestamps
_rate_limits = defaultdict(list)


def reset_rate_limits():
    """Reset rate limiter state (used in tests)."""
    _rate_limits.clear()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Validate Bearer token and return the authenticated User."""
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authentication token required.")
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired authentication token.")
    
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise UnauthorizedException("Invalid token payload structure.")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("User account not found.")
    
    if not user.is_active:
        raise ForbiddenException("Account has been deactivated.")
    
    return user


def rate_limit(limit_per_minute: int = 30):
    """Simple rate-limiting dependency by client IP / token."""
    def dependency(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
        x_forwarded_for: Optional[str] = Header(None)
    ):
        if settings.ENVIRONMENT == "testing":
            return True

        key = "anonymous"
        if credentials and credentials.credentials:
            key = credentials.credentials[-16:]
        elif x_forwarded_for:
            key = x_forwarded_for.split(",")[0].strip()
        
        now = datetime.now(timezone.utc)
        one_minute_ago = now - timedelta(minutes=1)
        
        timestamps = _rate_limits[key]
        _rate_limits[key] = [t for t in timestamps if t > one_minute_ago]
        
        if len(_rate_limits[key]) >= limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait a moment before trying again."
            )
        
        _rate_limits[key].append(now)
        return True

    return dependency
