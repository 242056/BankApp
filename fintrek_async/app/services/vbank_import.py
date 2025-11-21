from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fintrek_async.app.clients.vbank import get_vbank_client
from fintrek_async.app import models

class VBankImportService:
    def __init__(self):
        self.client = get_vbank_client()
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string from VBank API to datetime object"""
        if not date_str:
            return None
        
        # Try common date formats
        formats = [
            "%Y-%m-%d",  # 2023-10-25
            "%Y-%m-%dT%H:%M:%S",  # 2023-10-25T12:30:45
            "%Y-%m-%dT%H:%M:%S.%f",  # 2023-10-25T12:30:45.123456
            "%Y-%m-%dT%H:%M:%SZ",  # 2023-10-25T12:30:45Z
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If none of the formats work, return None
        return None

    async def fetch_accounts(self, db: AsyncSession, user_id):
        payload = await self.client.get_accounts()
        # ожидаем структуру наподобие {"accounts":[{id, iban, currency, balance, name, ...}, ...]}
        for a in payload.get("accounts", []):
            # находим/создаем account (привяжем к user_id)
            acc = await db.scalar(
                select(models.Account).where(models.Account.user_id == user_id, models.Account.external_id == a["id"])
            )
            if not acc:
                acc = models.Account(
                    user_id=user_id,
                    external_id=a["id"],
                    name=a.get("name") or a.get("product") or "VBank account",
                    account_name=a.get("name") or a.get("product") or "VBank account",
                    account_type=models.AccountType.CHECKING,  # Default to CHECKING
                    currency=a.get("currency") or "RUB",
                    balance=a.get("balance", 0),
                    provider="vbank",
                    status=models.AccountStatus.ACTIVE,
                )
                db.add(acc)
            else:
                acc.balance = a.get("balance", acc.balance)
                acc.currency = a.get("currency", acc.currency)
                acc.name = a.get("name") or acc.name
        await db.flush()

    async def fetch_transactions(self, db: AsyncSession, user_id, account_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None):
        # First, get the account to ensure it exists and belongs to the user
        account = await db.scalar(
            select(models.Account).where(
                models.Account.id == account_id,
                models.Account.user_id == user_id
            )
        )
        if not account:
            raise ValueError(f"Account {account_id} not found for user {user_id}")
        
        # Use the account's external_id to fetch transactions from VBank
        payload = await self.client.get_transactions(account.external_id or str(account_id), date_from=date_from, date_to=date_to)
        # ожидаем {"transactions":[{id, amount, currency, bookingDate, description, category, ...}, ...]}
        for t in payload.get("transactions", []):
            tx = await db.scalar(
                select(models.Transaction).where(
                    models.Transaction.user_id == user_id,
                    models.Transaction.external_id == t["id"],
                )
            )
            if not tx:
                tx = models.Transaction(
                    user_id=user_id,
                    account_id=account_id,  # Use the UUID account_id
                    external_id=t["id"],
                    amount=t.get("amount", 0),
                    currency=t.get("currency", "RUB"),
                    transaction_date=self._parse_date(t.get("bookingDate") or t.get("valueDate")),
                    description=t.get("description") or "",
                    category_guess=t.get("category"),
                    provider="vbank",
                    status=models.TransactionStatus.COMPLETED,
                    transaction_type=models.TransactionType.INCOME if float(t.get("amount", 0)) >= 0 else models.TransactionType.EXPENSE,
                )
                db.add(tx)
            else:
                tx.amount = t.get("amount", tx.amount)
                tx.description = t.get("description", tx.description)
        await db.flush()
