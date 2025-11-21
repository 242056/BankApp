"""
Эндпоинты для управления транзакциями
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, delete
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from fintrek_async.app.api.v1.deps import get_db, get_current_user
from fintrek_async.app.models.user import User
from fintrek_async.app.models.transaction import Transaction
from fintrek_async.app.models.account import Account
from fintrek_async.app.models.category import Category
from fintrek_async.app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    TransactionFilter
)

router = APIRouter()


@router.get("/", response_model=TransactionListResponse)
async def get_transactions(
    account_id: Optional[UUID] = Query(None, description="Фильтр по счету"),
    category_id: Optional[UUID] = Query(None, description="Фильтр по категории"),
    date_from: Optional[datetime] = Query(None, description="Начальная дата"),
    date_to: Optional[datetime] = Query(None, description="Конечная дата"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список транзакций с фильтрацией и пагинацией
    """
    # Базовый запрос
    stmt = select(Transaction).filter(
        Transaction.user_id == current_user.id
    )
    
    # Применить фильтры
    if account_id:
        stmt = stmt.filter(Transaction.account_id == account_id)
    
    if category_id:
        stmt = stmt.filter(Transaction.category_id == category_id)
    
    if date_from:
        stmt = stmt.filter(Transaction.transaction_date >= date_from)
    
    if date_to:
        stmt = stmt.filter(Transaction.transaction_date <= date_to)
    
    # Подсчитать общее количество
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    # Применить пагинацию и сортировку
    offset = (page - 1) * page_size
    stmt = stmt.order_by(
        Transaction.transaction_date.desc()
    ).offset(offset).limit(page_size)
    
    result = await db.execute(stmt)
    transactions = result.scalars().all()
    
    return TransactionListResponse(
        transactions=transactions,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о конкретной транзакции
    """
    transaction = (await db.execute(select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новую транзакцию вручную
    
    Требования:
    - account_id: обязательное поле, должен быть валидным UUID существующего счета пользователя
    - category_id: опциональное поле, если указан - должен быть валидным UUID
    - related_account_id: опциональное поле, используется для переводов между счетами
    """
    # Проверить что счет принадлежит пользователю
    account = (await db.execute(select(Account).where(
        Account.id == transaction_data.account_id,
        Account.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {transaction_data.account_id} not found or does not belong to current user"
        )
    
    # Если указан related_account_id (для переводов), проверить что он существует
    if transaction_data.related_account_id:
        related_account = (await db.execute(select(Account).where(
            Account.id == transaction_data.related_account_id,
            Account.user_id == current_user.id
        ))).scalar_one_or_none()
        
        if not related_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Related account with id {transaction_data.related_account_id} not found or does not belong to current user"
            )
    
    # Нормализуем datetime - убираем timezone для совместимости с TIMESTAMP WITHOUT TIME ZONE
    transaction_date = transaction_data.transaction_date
    if transaction_date.tzinfo is not None:
        # Если datetime имеет timezone, преобразуем в UTC и убираем timezone info
        transaction_date = transaction_date.astimezone(timezone.utc).replace(tzinfo=None)
    
    transaction = Transaction(
        user_id=current_user.id,
        account_id=transaction_data.account_id,
        category_id=transaction_data.category_id,
        transaction_type=transaction_data.transaction_type,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        description=transaction_data.description,
        merchant_name=transaction_data.merchant_name,
        notes=transaction_data.notes,
        transaction_date=transaction_date,
        related_account_id=transaction_data.related_account_id
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    transaction_data: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить транзакцию (например, изменить категорию или добавить заметки)
    
    Все поля опциональны. Передавайте только те поля, которые нужно обновить.
    Для category_id передайте валидный UUID существующей категории или null, чтобы убрать категорию.
    """
    transaction = (await db.execute(select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Обновить только переданные поля
    update_data = transaction_data.model_dump(exclude_unset=True)
    
    # Если указан category_id, проверить что категория существует
    if 'category_id' in update_data and update_data['category_id'] is not None:
        category = (await db.execute(select(Category).where(
            Category.id == update_data['category_id'],
            or_(
                Category.user_id == current_user.id,
                Category.user_id.is_(None)  # Системные категории
            )
        ))).scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {update_data['category_id']} not found or not accessible"
            )
    
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    await db.commit()
    await db.refresh(transaction)
    
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить транзакцию
    """
    transaction = (await db.execute(select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    await db.delete(transaction)
    await db.commit()
    
    return None
