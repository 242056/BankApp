"""
Сервис для работы с Open Banking API
"""
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import httpx
from fintrek_async.app.models.bank_connection import BankConnection, BankConnectionStatus
from fintrek_async.app.models.account import Account, AccountType, AccountStatus
from fintrek_async.app.models.transaction import Transaction, TransactionType, TransactionStatus
from fintrek_async.app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class OpenBankingService:
    """Сервис для интеграции с банковскими Open API"""
    
    def __init__(self):
        self.base_url = getattr(settings, "OPEN_BANKING_API_URL", "https://api.example-bank.ru")
        self.client_id = getattr(settings, "OPEN_BANKING_CLIENT_ID", "")
        self.client_secret = getattr(settings, "OPEN_BANKING_CLIENT_SECRET", "")
        self.timeout = 30.0
    
    async def initiate_oauth_flow(self, bank_name: str, redirect_uri: str) -> Dict[str, str]:
        """
        Инициировать OAuth 2.0 flow для подключения к банку
        
        Returns:
            Dict с authorization_url и state
        """
        # В реальной реализации здесь будет запрос к банковскому API
        # Для демонстрации возвращаем mock данные
        state = f"state_{datetime.utcnow().timestamp()}"
        
        authorization_url = (
            f"{self.base_url}/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=accounts transactions"
            f"&state={state}"
        )
        
        return {
            "authorization_url": authorization_url,
            "state": state
        }
    
    async def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Обменять authorization code на access и refresh токены
        
        Args:
            code: Authorization code от банка
            redirect_uri: Redirect URI для валидации
            
        Returns:
            Dict с access_token, refresh_token, expires_in
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/oauth/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Обновить access token используя refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict с новым access_token и expires_in
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/oauth/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise
    
    async def fetch_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Получить список счетов из банковского API
        
        Args:
            access_token: Access token для авторизации
            
        Returns:
            Список счетов
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/accounts",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("accounts", [])
        except Exception as e:
            logger.error(f"Error fetching accounts: {e}")
            raise
    
    async def fetch_transactions(
        self,
        access_token: str,
        account_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить транзакции для счета из банковского API
        
        Args:
            access_token: Access token для авторизации
            account_id: ID счета в банке
            date_from: Начальная дата
            date_to: Конечная дата
            
        Returns:
            Список транзакций
        """
        try:
            params = {}
            if date_from:
                params["date_from"] = date_from.isoformat()
            if date_to:
                params["date_to"] = date_to.isoformat()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/accounts/{account_id}/transactions",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("transactions", [])
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            raise
    
    def map_account_type(self, bank_account_type: str) -> AccountType:
        """
        Преобразовать тип счета из банковского API в наш тип
        
        Args:
            bank_account_type: Тип счета от банка
            
        Returns:
            AccountType
        """
        mapping = {
            "current": AccountType.CHECKING,
            "checking": AccountType.CHECKING,
            "savings": AccountType.SAVINGS,
            "credit_card": AccountType.CREDIT_CARD,
            "card": AccountType.CREDIT_CARD,
            "investment": AccountType.INVESTMENT,
            "loan": AccountType.LOAN,
        }
        return mapping.get(bank_account_type.lower(), AccountType.CHECKING)
    
    def map_transaction_type(self, bank_transaction_type: str, amount: float) -> TransactionType:
        """
        Преобразовать тип транзакции из банковского API в наш тип
        
        Args:
            bank_transaction_type: Тип транзакции от банка
            amount: Сумма транзакции
            
        Returns:
            TransactionType
        """
        if bank_transaction_type.lower() in ["transfer", "internal_transfer"]:
            return TransactionType.TRANSFER
        
        # Определяем по знаку суммы
        if amount > 0:
            return TransactionType.INCOME
        else:
            return TransactionType.EXPENSE


# Singleton instance
open_banking_service = OpenBankingService()
