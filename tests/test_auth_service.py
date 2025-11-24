"""Tests for authentication service."""
import pytest
from app.services.auth_service import auth_service
from app.repositories.user_repository import user_repository
from fastapi import HTTPException


def test_register_user_success(db_session):
    """Test successful user registration."""
    user = auth_service.register_user(
        db_session,
        email="test@example.com",
        password="password123",
        full_name="Test User"
    )
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.hashed_password != "password123"


def test_register_user_duplicate_email(db_session):
    """Test registration with duplicate email fails."""
    auth_service.register_user(
        db_session,
        email="test@example.com",
        password="password123",
        full_name="Test User"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service.register_user(
            db_session,
            email="test@example.com",
            password="password456",
            full_name="Another User"
        )
    
    assert exc_info.value.status_code == 409


def test_register_user_short_password(db_session):
    """Test registration with short password fails."""
    with pytest.raises(HTTPException) as exc_info:
        auth_service.register_user(
            db_session,
            email="test@example.com",
            password="short",
            full_name="Test User"
        )
    
    assert exc_info.value.status_code == 400


def test_authenticate_user_success(db_session):
    """Test successful user authentication."""
    auth_service.register_user(
        db_session,
        email="test@example.com",
        password="password123",
        full_name="Test User"
    )
    
    token, user = auth_service.authenticate_user(
        db_session,
        email="test@example.com",
        password="password123"
    )
    
    assert token is not None
    assert user.email == "test@example.com"


def test_authenticate_user_wrong_password(db_session):
    """Test authentication with wrong password fails."""
    auth_service.register_user(
        db_session,
        email="test@example.com",
        password="password123",
        full_name="Test User"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate_user(
            db_session,
            email="test@example.com",
            password="wrongpassword"
        )
    
    assert exc_info.value.status_code == 401


def test_authenticate_user_not_found(db_session):
    """Test authentication with non-existent user fails."""
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate_user(
            db_session,
            email="nonexistent@example.com",
            password="password123"
        )
    
    assert exc_info.value.status_code == 401
