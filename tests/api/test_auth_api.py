"""API tests for user registration, authentication, and session endpoints."""

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "WealthOS AI"


def test_user_registration_success(client):
    payload = {
        "email": "newuser@wealthos.ai",
        "password": "Password123!",
        "full_name": "New Investor",
        "preferred_currency": "USD"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@wealthos.ai"
    assert data["full_name"] == "New Investor"
    assert "id" in data
    assert "hashed_password" not in data  # Never leak hashed password


def test_user_registration_duplicate_email(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "AnyPassword123!",
        "full_name": "Duplicate User"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["error"] is True


def test_user_login_success(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "SecurePassword123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == test_user.email


def test_user_login_invalid_password(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "WrongPassword999!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["error"] is True


def test_get_current_user_profile_authenticated(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@wealthos.ai"
    assert data["preferred_currency"] == "USD"


def test_get_current_user_profile_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_update_user_settings(client, auth_headers):
    update_payload = {
        "full_name": "Alice Updated",
        "preferred_currency": "EUR",
        "monthly_income": "7500.00",
        "risk_tolerance": "aggressive"
    }
    response = client.put("/api/v1/users/profile", json=update_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Alice Updated"
    assert data["preferred_currency"] == "EUR"
    assert data["monthly_income"] == "7500.00"
    assert data["risk_tolerance"] == "aggressive"
