"""
Тесты для эндпоинтов аналитики
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime


def test_get_spending_by_category_unauthorized(client: TestClient):
    """
    Тест доступа к аналитике без авторизации
    """
    response = client.get("/api/v1/analytics/spending-by-category")
    assert response.status_code == 401


def test_get_spending_by_category(client: TestClient, auth_headers):
    """
    Тест получения расходов по категориям
    """
    response = client.get(
        "/api/v1/analytics/spending-by-category",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "period" in data
    assert "total_spending" in data
    assert "categories" in data
    assert isinstance(data["categories"], list)


def test_get_income_vs_expenses(client: TestClient, auth_headers):
    """
    Тест получения сравнения доходов и расходов
    """
    response = client.get(
        "/api/v1/analytics/income-vs-expenses?months=6",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "months" in data
    assert data["months"] == 6
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_account_summary(client: TestClient, auth_headers):
    """
    Тест получения сводки по счетам
    """
    response = client.get(
        "/api/v1/analytics/account-summary",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_balance" in data
    assert "accounts_count" in data
    assert "accounts" in data
    assert isinstance(data["accounts"], list)


def test_get_transaction_statistics(client: TestClient, auth_headers):
    """
    Тест получения статистики транзакций
    """
    response = client.get(
        "/api/v1/analytics/transaction-statistics?days=30",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "period_days" in data
    assert data["period_days"] == 30
    assert "total_transactions" in data
    assert "income" in data
    assert "expenses" in data
    assert "net_income" in data


def test_get_daily_spending_trend(client: TestClient, auth_headers):
    """
    Тест получения тренда ежедневных расходов
    """
    response = client.get(
        "/api/v1/analytics/daily-spending-trend?days=30",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "period_days" in data
    assert data["period_days"] == 30
    assert "average_daily_spending" in data
    assert "total_spending" in data
    assert "daily_data" in data
    assert isinstance(data["daily_data"], list)


def test_analytics_with_invalid_parameters(client: TestClient, auth_headers):
    """
    Тест аналитики с невалидными параметрами
    """
    # Слишком много месяцев
    response = client.get(
        "/api/v1/analytics/income-vs-expenses?months=100",
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error
    
    # Отрицательное количество дней
    response = client.get(
        "/api/v1/analytics/transaction-statistics?days=-5",
        headers=auth_headers
    )
    assert response.status_code == 422
