"""
Эндпоинты для управления подключениями к банкам
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from fintrek_async.app.api.v1.deps import get_db, get_current_user
from fintrek_async.app.models.user import User
from fintrek_async.app.models.bank_connection import BankConnection, BankConnectionStatus
from fintrek_async.app.schemas.bank_connection import (
    BankConnectionCreate,
    BankConnectionResponse,
    BankConnectionListResponse,
    BankConnectionSync,
    BankConnectionSyncResponse
)
from fintrek_async.app.services.sync_service import sync_service

router = APIRouter()


@router.get("/", response_model=BankConnectionListResponse)
async def get_bank_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список всех подключений к банкам
    """
    connections = (await db.execute(select(BankConnection).where(
        BankConnection.user_id == current_user.id
    ))).scalars().all()
    
    return BankConnectionListResponse(
        connections=connections,
        total=len(connections)
    )


@router.get("/{connection_id}", response_model=BankConnectionResponse)
async def get_bank_connection(
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о конкретном подключении
    """
    connection = (await db.execute(select(BankConnection).where(
        BankConnection.id == connection_id,
        BankConnection.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank connection not found"
        )
    
    return connection


@router.post("/", response_model=BankConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_connection(
    connection_data: BankConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новое подключение к банку
    
    Примечание: В реальной реализации здесь должен быть OAuth flow
    """
    connection = BankConnection(
        user_id=current_user.id,
        bank_name=connection_data.bank_name,
        bank_bic=connection_data.bank_bic,
        status=BankConnectionStatus.ACTIVE
    )
    
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    
    return connection


@router.post("/sync", response_model=BankConnectionSyncResponse)
async def sync_bank_connection(
    sync_data: BankConnectionSync,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Синхронизировать данные с банком
    """
    # Проверить что подключение принадлежит пользователю
    connection = (await db.execute(select(BankConnection).where(
        BankConnection.id == sync_data.connection_id,
        BankConnection.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank connection not found"
        )
    
    # Выполнить синхронизацию
    result = await sync_service.sync_bank_connection(
        db=db,
        connection_id=str(sync_data.connection_id),
        user_id=str(current_user.id)
    )
    
    return BankConnectionSyncResponse(**result)


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bank_connection(
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отключить и удалить подключение к банку
    """
    connection = (await db.execute(select(BankConnection).where(
        BankConnection.id == connection_id,
        BankConnection.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank connection not found"
        )
    
    # Изменить статус на отключено
    connection.status = BankConnectionStatus.DISCONNECTED
    await db.commit()
    
    # Можно также удалить подключение полностью
    # await await db.delete(connection)
    # await await db.commit()
    
    return None
