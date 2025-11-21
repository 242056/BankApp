"""
Тесты для эндпоинтов аутентификации
"""
import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """
    Тест регистрации нового пользователя
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data


def test_register_duplicate_email(client: TestClient):
    """
    Тест регистрации с уже существующим email
    """
    # Первая регистрация
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    # Попытка повторной регистрации
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "anotherpassword",
            "full_name": "Another User"
        }
    )
    
    assert response.status_code == 400
    assert "уже зарегистрирован" in response.json()["detail"]


def test_login_success(client: TestClient):
    """
    Тест успешного входа
    """
    # Регистрация пользователя
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    # Вход
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    """
    Тест входа с неправильным паролем
    """
    # Регистрация пользователя
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    # Попытка входа с неправильным паролем
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401


def test_login_nonexistent_user(client: TestClient):
    """
    Тест входа несуществующего пользователя
    """
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "somepassword"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user(client: TestClient):
    """
    Тест получения информации о текущем пользователе
    """
    # Регистрация и вход
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Получение информации о пользователе
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


def test_access_protected_endpoint_without_token(client: TestClient):
    """
    Тест доступа к защищенному эндпоинту без токена
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
