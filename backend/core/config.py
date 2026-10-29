"""Application configuration and settings for WealthOS AI."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


def _load_env_file(filepath: Path) -> None:
    """Simple, safe .env loader that populates os.environ if not already set."""
    if not filepath.exists():
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


# Load .env from project root if present
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
_load_env_file(_env_path)


class Settings(BaseModel):
    APP_NAME: str = "WealthOS AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() in ("true", "1", "yes"))
    
    # Security & JWT
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", 
            "wealthos-development-secret-key-must-be-changed-in-production-32-chars-min"
        )
    )
    ALGORITHM: str = Field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    )
    
    # Database URL
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./wealthos.db")
    )
    
    # Host & Ports
    BACKEND_HOST: str = Field(default_factory=lambda: os.getenv("BACKEND_HOST", "127.0.0.1"))
    BACKEND_PORT: int = Field(default_factory=lambda: int(os.getenv("BACKEND_PORT", "8000")))
    FRONTEND_PORT: int = Field(default_factory=lambda: int(os.getenv("FRONTEND_PORT", "8501")))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # AI Assistant
    AI_PROVIDER: str = Field(default_factory=lambda: os.getenv("AI_PROVIDER", "gemini"))
    GEMINI_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    AI_MODEL_NAME: str = Field(default_factory=lambda: os.getenv("AI_MODEL_NAME", "gemini-1.5-flash"))
    
    # Market Data
    ALPHA_VANTAGE_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("ALPHA_VANTAGE_API_KEY"))
    FINNHUB_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("FINNHUB_API_KEY"))
    
    # Rate Limiting & Safety
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 15
    MAX_CSV_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB


settings = Settings()
