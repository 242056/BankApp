"""
Сервис синхронизации данных с банками
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
from uuid import UUID
import logging

from fintrek_async.app.models.bank_connection import BankConnection, BankConnectionStatus
from fintrek_async.app.models.account import Account, AccountType, AccountStatus
from fintrek_async.app.models.transaction import Transaction, TransactionType, TransactionStatus
from fintrek_async.app.services.open_banking_service import open_banking_service
from fintrek_async.app.core.security import decrypt_token, encrypt_token

logger = logging.getLogger(__name__)


class SyncService:
    """Сервис для синхронизации данных с банковскими API"""
    
    async def sync_bank_connection(
        self,
        db: AsyncSession,
        connection_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Синхронизировать данные для конкретного подключения к банку
        
        Args:
            db: Database session
            connection_id: ID подключения к банку
            user_id: ID пользователя
            
        Returns:
            Dict с результатами синхронизации
        """
        # Получить подключение
        stmt = select(BankConnection).filter(
            BankConnection.id == UUID(connection_id),
            BankConnection.user_id == UUID(user_id)
        )
        result = await db.execute(stmt)
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise ValueError("Bank connection not found")
        
        if connection.status == BankConnectionStatus.DISCONNECTED:
            raise ValueError("Bank connection is disconnected")
        
        accounts_synced = 0
        transactions_synced = 0
        
        try:
            # Проверить и обновить токен если нужно
            access_token = await self._ensure_valid_token(db, connection)
            
            # Синхронизировать счета
            accounts_synced = await self._sync_accounts(db, connection, access_token)
            
            # Синхронизировать транзакции для каждого счета
            transactions_synced = await self._sync_transactions(db, connection, access_token)
            
            # Обновить время последней синхронизации
            connection.last_synced_at = datetime.utcnow()
            connection.status = BankConnectionStatus.ACTIVE
            connection.last_error = None
            await db.commit()
            
            return {
                "success": True,
                "message": "Synchronization completed successfully",
                "accounts_synced": accounts_synced,
                "transactions_synced": transactions_synced
            }
            
        except Exception as e:
            logger.error(f"Error syncing bank connection {connection_id}: {e}")
            connection.status = BankConnectionStatus.ERROR
            connection.last_error = str(e)
            await db.commit()
            
            return {
                "success": False,
                "message": f"Synchronization failed: {str(e)}",
                "accounts_synced": accounts_synced,
                "transactions_synced": transactions_synced
            }
    
    async def _ensure_valid_token(self, db: AsyncSession, connection: BankConnection) -> str:
        """
        Убедиться что access token валиден, обновить если нужно
        
        Args:
            db: Database session
            connection: BankConnection объект
            
        Returns:
            Валидный access token
        """
        # Расшифровать токен
        access_token = decrypt_token(connection.access_token_encrypted)
        
        # Проверить срок действия
        if connection.token_expires_at and connection.token_expires_at < datetime.utcnow():
            # Токен истек, обновить
            refresh_token = decrypt_token(connection.refresh_token_encrypted)
            
            tokens = await open_banking_service.refresh_access_token(refresh_token)
            
            # Обновить токены в БД
            connection.access_token_encrypted = encrypt_token(tokens["access_token"])
            if "refresh_token" in tokens:
                connection.refresh_token_encrypted = encrypt_token(tokens["refresh_token"])
            
            connection.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
            await db.commit()
            
            access_token = tokens["access_token"]
        
        return access_token
    
    async def _sync_accounts(
        self,
        db: AsyncSession,
        connection: BankConnection,
        access_token: str
    ) -> int:
        """
        Синхронизировать счета
        
        Args:
            db: Database session
            connection: BankConnection объект
            access_token: Access token
            
        Returns:
            Количество синхронизированных счетов
        """
        # Получить счета из банковского API
        bank_accounts = await open_banking_service.fetch_accounts(access_token)
        
        synced_count = 0
        
        for bank_account in bank_accounts:
            # Проверить существует ли счет
            stmt = select(Account).filter(
                Account.bank_connection_id == connection.id,
                Account.account_number == bank_account.get("account_number")
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()
            
            if account:
                # Обновить существующий счет
                account.balance = Decimal(str(bank_account.get("balance", 0)))
                account.available_balance = Decimal(str(bank_account.get("available_balance", 0))) if bank_account.get("available_balance") else None
                account.last_synced_at = datetime.utcnow()
                account.status = AccountStatus.ACTIVE
                account.sync_error = None
            else:
                # Создать новый счет
                account = Account(
                    user_id=connection.user_id,
                    bank_connection_id=connection.id,
                    account_name=bank_account.get("name", f"{connection.bank_name} Account"),
                    account_number=bank_account.get("account_number"),
                    account_type=open_banking_service.map_account_type(bank_account.get("type", "checking")),
                    currency=bank_account.get("currency", "RUB"),
                    balance=Decimal(str(bank_account.get("balance", 0))),
                    available_balance=Decimal(str(bank_account.get("available_balance", 0))) if bank_account.get("available_balance") else None,
                    status=AccountStatus.ACTIVE,
                    last_synced_at=datetime.utcnow()
                )
                db.add(account)
            
            synced_count += 1
        
        await db.commit()
        return synced_count
    
    async def _sync_transactions(
        self,
        db: AsyncSession,
        connection: BankConnection,
        access_token: str
    ) -> int:
        """
        Синхронизировать транзакции для всех счетов подключения
        
        Args:
            db: Database session
            connection: BankConnection объект
            access_token: Access token
            
        Returns:
            Количество синхронизированных транзакций
        """
        # Получить все счета этого подключения
        stmt = select(Account).filter(
            Account.bank_connection_id == connection.id
        )
        result = await db.execute(stmt)
        accounts = result.scalars().all()
        
        synced_count = 0
        
        # Синхронизировать транзакции за последние 30 дней
        date_from = datetime.utcnow() - timedelta(days=30)
        
        for account in accounts:
            if not account.account_number:
                continue
            
            try:
                # Получить транзакции из банковского API
                bank_transactions = await open_banking_service.fetch_transactions(
                    access_token,
                    account.account_number,
                    date_from=date_from
                )
                
                for bank_txn in bank_transactions:
                    external_id = bank_txn.get("id")
                    
                    # Проверить существует ли транзакция
                    stmt = select(Transaction).filter(
                        Transaction.external_id == external_id
                    )
                    result = await db.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        continue  # Транзакция уже существует
                    
                    # Создать новую транзакцию
                    amount = Decimal(str(abs(bank_txn.get("amount", 0))))
                    transaction_type = open_banking_service.map_transaction_type(
                        bank_txn.get("type", ""),
                        float(bank_txn.get("amount", 0))
                    )
                    
                    transaction = Transaction(
                        user_id=connection.user_id,
                        account_id=account.id,
                        transaction_type=transaction_type,
                        amount=amount,
                        currency=bank_txn.get("currency", "RUB"),
                        description=bank_txn.get("description"),
                        merchant_name=bank_txn.get("merchant_name"),
                        transaction_date=datetime.fromisoformat(bank_txn.get("date")) if bank_txn.get("date") else datetime.utcnow(),
                        posted_date=datetime.fromisoformat(bank_txn.get("posted_date")) if bank_txn.get("posted_date") else None,
                        status=TransactionStatus.COMPLETED,
                        external_id=external_id
                    )
                    db.add(transaction)
                    synced_count += 1
                
            except Exception as e:
                logger.error(f"Error syncing transactions for account {account.id}: {e}")
                account.sync_error = str(e)
        
        await db.commit()
        return synced_count


# Singleton instance
sync_service = SyncService()
