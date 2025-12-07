"""API Integration tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_register_user_success(self, test_client: TestClient):
        """Test successful user registration."""
        # Arrange
        payload = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "full_name": "New User"
        }
        
        # Act
        response = test_client.post("/v1/auth/register", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["full_name"] == payload["full_name"]
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_register_user_duplicate_email(self, test_client: TestClient, test_user):
        """Test registration with existing email returns 409."""
        # Arrange
        payload = {
            "email": test_user.email,  # Already exists
            "password": "password123",
            "full_name": "Duplicate User"
        }
        
        # Act
        response = test_client.post("/v1/auth/register", json=payload)
        
        # Assert
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_user_invalid_password(self, test_client: TestClient):
        """Test registration with weak password returns 400."""
        # Arrange
        payload = {
            "email": "weak@example.com",
            "password": "123",  # Too short
            "full_name": "Weak Password User"
        }
        
        # Act
        response = test_client.post("/v1/auth/register", json=payload)
        
        # Assert
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()
    
    def test_login_success(self, test_client: TestClient, test_user):
        """Test successful login returns access token."""
        # Arrange
        payload = {
            "email": test_user.email,
            "password": "password123"
        }
        
        # Act
        response = test_client.post("/v1/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, test_client: TestClient, test_user):
        """Test login with wrong password returns 401."""
        # Arrange
        payload = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        # Act
        response = test_client.post("/v1/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower() or "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, test_client: TestClient):
        """Test login with non-existent email returns 401."""
        # Arrange
        payload = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        # Act
        response = test_client.post("/v1/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 401
    
    def test_get_current_user_without_token(self, test_client: TestClient):
        """Test accessing protected endpoint without token returns 401 or 403."""
        # Act
        response = test_client.get("/v1/auth/me")
        
        # Assert
        assert response.status_code in [401, 403]
    
    def test_get_current_user_with_valid_token(
        self, test_client: TestClient, test_user, auth_headers
    ):
        """Test accessing protected endpoint with valid token succeeds."""
        # Act
        response = test_client.get("/v1/auth/me", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
    
    def test_get_current_user_with_invalid_token(self, test_client: TestClient):
        """Test accessing protected endpoint with invalid token returns 401."""
        # Arrange
        headers = {"Authorization": "Bearer invalid_token_here"}
        
        # Act
        response = test_client.get("/v1/auth/me", headers=headers)
        
        # Assert
        assert response.status_code == 401
