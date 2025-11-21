"""
API эндпоинты для AI-инсайтов и рекомендаций
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fintrek_async.app.api.v1.deps import get_db, get_current_user
from fintrek_async.app.models.user import User
from fintrek_async.app.ml.transaction_categorizer import transaction_categorizer
from fintrek_async.app.ml.spending_analyzer import spending_analyzer
from fintrek_async.app.ml.recommendation_engine import recommendation_engine
from fintrek_async.app.ml.forecasting_model import forecasting_model
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/categorize-transactions")
async def categorize_transactions(
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Автоматически категоризировать некатегоризированные транзакции
    """
    count = await transaction_categorizer.batch_categorize(db, limit=limit)
    
    return {
        "message": f"Категоризировано {count} транзакций",
        "categorized_count": count
    }


@router.get("/spending-by-category")
async def get_spending_by_category(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить расходы по категориям за период
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    spending = await spending_analyzer.get_spending_by_category(
        db, str(current_user.id), start_date, end_date
    )
    
    # Преобразовать в список для удобства визуализации
    spending_list = [
        {"category": category, "amount": amount}
        for category, amount in spending.items()
    ]
    
    # Сортировать по сумме
    spending_list.sort(key=lambda x: x['amount'], reverse=True)
    
    total = sum(item['amount'] for item in spending_list)
    
    return {
        "period_days": days,
        "total_spending": round(total, 2),
        "categories": spending_list
    }


@router.get("/monthly-spending")
async def get_monthly_spending(
    months: int = Query(6, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить расходы по месяцам
    """
    monthly_data = await spending_analyzer.get_monthly_spending(
        db, str(current_user.id), months=months
    )
    
    return {
        "months": months,
        "data": monthly_data
    }


@router.get("/recurring-payments")
async def get_recurring_payments(
    min_occurrences: int = Query(3, ge=2, le=10),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список повторяющихся платежей (подписки)
    """
    recurring = await spending_analyzer.detect_recurring_payments(
        db, str(current_user.id), min_occurrences=min_occurrences
    )
    
    total_monthly = sum(item['amount'] for item in recurring)
    
    return {
        "recurring_payments": recurring,
        "total_count": len(recurring),
        "estimated_monthly_cost": round(total_monthly, 2)
    }


@router.get("/anomalies")
async def get_anomalies(
    threshold: float = Query(2.0, ge=1.0, le=5.0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список аномальных транзакций
    """
    anomalies = await spending_analyzer.detect_anomalies(
        db, str(current_user.id), threshold_multiplier=threshold
    )
    
    return {
        "anomalies": anomalies,
        "count": len(anomalies)
    }


@router.get("/spending-trends")
async def get_spending_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить тренды расходов (сравнение текущего и предыдущего месяца)
    """
    trends = await spending_analyzer.get_spending_trends(
        db, str(current_user.id)
    )
    
    return trends


@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить персонализированные рекомендации
    """
    recommendations = await recommendation_engine.generate_recommendations(
        db, str(current_user.id)
    )
    
    return {
        "recommendations": recommendations,
        "count": len(recommendations)
    }


@router.get("/proactive-advice/{scenario}")
async def get_proactive_advice(
    scenario: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить проактивный совет для конкретного сценария
    
    Доступные сценарии: coffee, subscription, etc.
    """
    advice = await recommendation_engine.generate_proactive_advice(
        db, str(current_user.id), scenario
    )
    
    return advice


@router.get("/forecast/spending")
async def forecast_spending(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Прогноз расходов на следующий месяц
    """
    forecast = await forecasting_model.forecast_next_month_spending(
        db, str(current_user.id)
    )
    
    return forecast


@router.get("/forecast/income")
async def forecast_income(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Прогноз дохода на следующий месяц
    """
    forecast = await forecasting_model.forecast_next_month_income(
        db, str(current_user.id)
    )
    
    return forecast


@router.get("/forecast/balance")
async def forecast_balance(
    months: int = Query(3, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Прогноз баланса на несколько месяцев вперед
    """
    forecast = await forecasting_model.forecast_balance(
        db, str(current_user.id), months_ahead=months
    )
    
    return {
        "months_ahead": months,
        "forecast": forecast
    }


@router.get("/financial-health")
async def get_financial_health(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить показатель финансового здоровья (0-100)
    """
    health_score = await forecasting_model.calculate_financial_health_score(
        db, str(current_user.id)
    )
    
    return health_score


@router.get("/dashboard")
async def get_ai_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить сводную информацию для AI-дашборда
    """
    # Собрать все данные
    health_score = await forecasting_model.calculate_financial_health_score(
        db, str(current_user.id)
    )
    
    recommendations = await recommendation_engine.generate_recommendations(
        db, str(current_user.id)
    )
    
    trends = await spending_analyzer.get_spending_trends(
        db, str(current_user.id)
    )
    
    spending_forecast = await forecasting_model.forecast_next_month_spending(
        db, str(current_user.id)
    )
    
    income_forecast = await forecasting_model.forecast_next_month_income(
        db, str(current_user.id)
    )
    
    return {
        "financial_health": health_score,
        "top_recommendations": recommendations[:3],  # Топ-3 рекомендации
        "spending_trends": trends,
        "next_month_forecast": {
            "spending": spending_forecast,
            "income": income_forecast
        }
    }
