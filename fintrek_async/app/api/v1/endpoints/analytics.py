"""
API эндпоинты для аналитики и агрегированных данных
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from datetime import datetime, timedelta
from fastapi_cache.decorator import cache

from fintrek_async.app.api.v1.deps import get_db, get_current_user
from fintrek_async.app.models.user import User
from fintrek_async.app.models.transaction import Transaction, TransactionType
from fintrek_async.app.models.category import Category
from fintrek_async.app.models.account import Account

router = APIRouter()


@router.get("/spending-by-category")
@cache(expire=300)  # Кэш на 5 минут
async def get_spending_by_category(
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить расходы по категориям за период
    
    Возвращает агрегированные данные о расходах, сгруппированные по категориям.
    Если даты не указаны, используется последние 30 дней.
    """
    # Установить даты по умолчанию
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Запрос с группировкой по категориям
    stmt = select(
        Category.name.label('category'),
        Category.category_type.label('type'),
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count'),
        func.avg(Transaction.amount).label('average')
    ).join(
        Transaction, Transaction.category_id == Category.id
    ).join(
        Account, Transaction.account_id == Account.id
    ).filter(
        and_(
            Account.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            Transaction.transaction_type == TransactionType.EXPENSE
        )
    ).group_by(
        Category.id, Category.name, Category.category_type
    ).order_by(
        func.sum(Transaction.amount).desc()
    )
    
    result = await db.execute(stmt)
    results = result.all()
    
    # Форматировать результаты
    spending_data = []
    total_spending = 0
    
    for row in results:
        amount = float(row.total)
        total_spending += amount
        spending_data.append({
            "category": row.category,
            "type": row.type,
            "total": round(amount, 2),
            "count": row.count,
            "average": round(float(row.average), 2)
        })
    
    # Добавить процентное соотношение
    for item in spending_data:
        item['percentage'] = round((item['total'] / total_spending * 100), 2) if total_spending > 0 else 0
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": (end_date - start_date).days
        },
        "total_spending": round(total_spending, 2),
        "categories": spending_data
    }


@router.get("/income-vs-expenses")
@cache(expire=300)  # Кэш на 5 минут
async def get_income_vs_expenses(
    months: int = Query(6, ge=1, le=24, description="Количество месяцев"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить сравнение доходов и расходов по месяцам
    
    Возвращает помесячные данные о доходах и расходах для построения графиков.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 30)
    
    # Запрос с группировкой по месяцам и типу транзакции
    stmt = select(
        extract('year', Transaction.transaction_date).label('year'),
        extract('month', Transaction.transaction_date).label('month'),
        Transaction.transaction_type,
        func.sum(Transaction.amount).label('total')
    ).join(
        Account, Transaction.account_id == Account.id
    ).filter(
        and_(
            Account.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )
    ).group_by(
        extract('year', Transaction.transaction_date),
        extract('month', Transaction.transaction_date),
        Transaction.transaction_type
    ).order_by(
        extract('year', Transaction.transaction_date),
        extract('month', Transaction.transaction_date)
    )
    
    result = await db.execute(stmt)
    results = result.all()
    
    # Организовать данные по месяцам
    monthly_data = {}
    for row in results:
        month_key = f"{int(row.year)}-{int(row.month):02d}"
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "month": month_key,
                "income": 0,
                "expenses": 0,
                "net": 0
            }
        
        amount = float(row.total)
        if row.transaction_type == TransactionType.INCOME:
            monthly_data[month_key]['income'] = round(amount, 2)
        elif row.transaction_type == TransactionType.EXPENSE:
            monthly_data[month_key]['expenses'] = round(amount, 2)
    
    # Вычислить чистый доход
    for month_data in monthly_data.values():
        month_data['net'] = round(month_data['income'] - month_data['expenses'], 2)
    
    # Преобразовать в список и отсортировать
    result_list = sorted(monthly_data.values(), key=lambda x: x['month'])
    
    return {
        "months": months,
        "data": result_list
    }


@router.get("/account-summary")
@cache(expire=60)  # Кэш на 1 минуту
async def get_account_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить сводку по всем счетам пользователя
    
    Возвращает общий баланс, количество счетов и распределение средств.
    """
    stmt = select(Account).filter(Account.user_id == current_user.id)
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    
    total_balance = 0
    accounts_data = []
    
    for account in accounts:
        balance = float(account.balance)
        total_balance += balance
        accounts_data.append({
            "id": str(account.id),
            "name": account.account_name,
            "type": account.account_type,
            "balance": round(balance, 2),
            "currency": account.currency
        })
    
    # Добавить процентное соотношение
    for account_data in accounts_data:
        account_data['percentage'] = round(
            (account_data['balance'] / total_balance * 100), 2
        ) if total_balance > 0 else 0
    
    return {
        "total_balance": round(total_balance, 2),
        "accounts_count": len(accounts),
        "accounts": accounts_data
    }


@router.get("/transaction-statistics")
@cache(expire=300)  # Кэш на 5 минут
async def get_transaction_statistics(
    days: int = Query(30, ge=1, le=365, description="Количество дней"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить статистику по транзакциям за период
    
    Возвращает общее количество транзакций, средние суммы и другие метрики.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Получить все транзакции пользователя за период
    stmt = select(Transaction).join(
        Account, Transaction.account_id == Account.id
    ).filter(
        and_(
            Account.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )
    )
    
    result = await db.execute(stmt)
    transactions = result.scalars().all()
    
    # Вычислить статистику
    total_count = len(transactions)
    income_transactions = [t for t in transactions if t.transaction_type == TransactionType.INCOME]
    expense_transactions = [t for t in transactions if t.transaction_type == TransactionType.EXPENSE]
    
    total_income = sum(float(t.amount) for t in income_transactions)
    total_expenses = sum(float(t.amount) for t in expense_transactions)
    
    avg_income = total_income / len(income_transactions) if income_transactions else 0
    avg_expense = total_expenses / len(expense_transactions) if expense_transactions else 0
    
    # Найти самую большую транзакцию
    largest_expense = max(
        (float(t.amount) for t in expense_transactions),
        default=0
    )
    largest_income = max(
        (float(t.amount) for t in income_transactions),
        default=0
    )
    
    return {
        "period_days": days,
        "total_transactions": total_count,
        "income": {
            "count": len(income_transactions),
            "total": round(total_income, 2),
            "average": round(avg_income, 2),
            "largest": round(largest_income, 2)
        },
        "expenses": {
            "count": len(expense_transactions),
            "total": round(total_expenses, 2),
            "average": round(avg_expense, 2),
            "largest": round(largest_expense, 2)
        },
        "net_income": round(total_income - total_expenses, 2)
    }


@router.get("/daily-spending-trend")
@cache(expire=600)  # Кэш на 10 минут
async def get_daily_spending_trend(
    days: int = Query(30, ge=7, le=90, description="Количество дней"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить тренд ежедневных расходов
    
    Возвращает расходы по дням для построения графика тренда.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Запрос с группировкой по дням
    stmt = select(
        func.date(Transaction.transaction_date).label('date'),
        func.sum(Transaction.amount).label('total')
    ).join(
        Account, Transaction.account_id == Account.id
    ).filter(
        and_(
            Account.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            Transaction.transaction_type == TransactionType.EXPENSE
        )
    ).group_by(
        func.date(Transaction.transaction_date)
    ).order_by(
        func.date(Transaction.transaction_date)
    )
    
    result = await db.execute(stmt)
    results = result.all()
    
    # Форматировать результаты
    daily_data = [
        {
            "date": row.date.isoformat(),
            "amount": round(float(row.total), 2)
        }
        for row in results
    ]
    
    # Вычислить среднее
    total = sum(item['amount'] for item in daily_data)
    average = total / len(daily_data) if daily_data else 0
    
    return {
        "period_days": days,
        "average_daily_spending": round(average, 2),
        "total_spending": round(total, 2),
        "daily_data": daily_data
    }
