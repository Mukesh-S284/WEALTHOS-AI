"""Pytest fixtures for WealthOS AI testing."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.core.config import settings
from backend.core.database import Base, get_db
from backend.main import app
from backend.core.security import hash_password
from backend.models.user import User

# Set testing environment
settings.ENVIRONMENT = "testing"

from sqlalchemy.pool import StaticPool

# In-memory SQLite for high-speed, isolated test runs using StaticPool so all connections share the memory DB
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Provide FastAPI test client with overridden database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a default test user."""
    user = User(
        email="testuser@wealthos.ai",
        hashed_password=hash_password("SecurePassword123!"),
        full_name="Alice Wealth",
        preferred_currency="USD",
        monthly_income="6500.00",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def second_user(db_session):
    """Create a second distinct user for multi-tenant isolation testing."""
    user = User(
        email="seconduser@wealthos.ai",
        hashed_password=hash_password("AnotherPassword456!"),
        full_name="Bob Isolation",
        preferred_currency="EUR",
        monthly_income="4000.00",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """Obtain valid JWT auth headers for test_user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@wealthos.ai", "password": "SecurePassword123!"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def second_auth_headers(client, second_user):
    """Obtain valid JWT auth headers for second_user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "seconduser@wealthos.ai", "password": "AnotherPassword456!"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
