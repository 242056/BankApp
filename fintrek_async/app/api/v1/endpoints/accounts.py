"""
Эндпоинты для управления счетами
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
from uuid import UUID

from fintrek_async.app.api.v1.deps import get_db, get_current_user
from fintrek_async.app.models.user import User
from fintrek_async.app.models.account import Account
from fintrek_async.app.schemas.account import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountListResponse
)

router = APIRouter()


@router.get("/", response_model=AccountListResponse)
async def get_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список всех счетов пользователя
    """
    accounts = (await db.execute(select(Account).where(
        Account.user_id == current_user.id
    ))).scalars().all()
    
    return AccountListResponse(
        accounts=accounts,
        total=len(accounts)
    )


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о конкретном счете
    """
    account = (await db.execute(select(Account).where(
        Account.id == account_id,
        Account.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый счет вручную (не через банковское API)
    """
    account = Account(
        user_id=current_user.id,
        account_name=account_data.account_name,
        account_type=account_data.account_type,
        currency=account_data.currency,
        balance=account_data.balance,
        account_number=account_data.account_number
    )
    
    db.add(account)
    await db.commit()
    await db.refresh(account)
    
    return account


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: UUID,
    account_data: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить информацию о счете
    """
    account = (await db.execute(select(Account).where(
        Account.id == account_id,
        Account.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Обновить только переданные поля
    update_data = account_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    await db.commit()
    await db.refresh(account)
    
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить счет
    """
    account = (await db.execute(select(Account).where(
        Account.id == account_id,
        Account.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    await db.delete(account)
    await db.commit()
    
    return None
