"""Unit tests for security, password hashing, and token operations."""

import time
from datetime import timedelta
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


def test_password_hashing_and_verification():
    plain = "SuperSecret123!"
    hashed = hash_password(plain)
    
    # Must be hashed and not plaintext
    assert hashed != plain
    assert hashed.startswith("$2b$")
    
    # Verification tests
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False


def test_token_creation_and_decoding():
    payload = {"sub": "user-uuid-1234", "user_id": "user-uuid-1234", "role": "user"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=5))
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-uuid-1234"
    assert decoded["user_id"] == "user-uuid-1234"
    assert decoded["role"] == "user"


def test_expired_token_handling():
    payload = {"sub": "user-uuid-1234"}
    # Token expired 1 minute ago
    token = create_access_token(payload, expires_delta=timedelta(seconds=-60))
    decoded = decode_access_token(token)
    assert decoded is None


def test_tampered_token_handling():
    payload = {"sub": "user-uuid-1234"}
    token = create_access_token(payload)
    # Tamper with the token string
    tampered = token[:-4] + "fake"
    decoded = decode_access_token(tampered)
    assert decoded is None
