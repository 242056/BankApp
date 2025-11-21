from __future__ import annotations
import asyncio
import time
from typing import Any, Dict, Optional

import httpx
from fintrek_async.app.core.config import settings
from fintrek_async.app.core.exceptions import VBankAPIError
import logging

logger = logging.getLogger(__name__)

class VBankAuth:
    def __init__(self, base_url: str, client_id: str, client_secret: str, bank_code: str):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.bank_code = bank_code
        self._access_token: Optional[str] = None
        self._exp_ts: float = 0.0
        self._lock = asyncio.Lock()

    async def token(self, http: httpx.AsyncClient) -> str:
        async with self._lock:
            now = time.time()
            if self._access_token and now < self._exp_ts - 30:
                return self._access_token

            try:
                # Шаг 1: получить bank-token
                # По их docs — POST /auth/bank-token (Bearer не требуется)
                # client_id и client_secret передаются в query params
                params = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }
                payload = {
                    "bank": self.bank_code,
                }
                resp = await http.post(f"{self.base_url}/auth/bank-token", params=params, json=payload, timeout=20.0)
                resp.raise_for_status()
                data = resp.json()
                # типичные поля: access_token / expires_in
                self._access_token = data.get("access_token") or data.get("token")
                ttl = int(data.get("expires_in", 1800))
                self._exp_ts = now + ttl
                return self._access_token
                
            except httpx.HTTPStatusError as e:
                logger.error(f"VBank auth HTTP error: {e.response.status_code} - {e.response.text}")
                raise VBankAPIError(
                    f"VBank authentication failed: {e.response.status_code}",
                    status_code=e.response.status_code,
                    details={"response": e.response.text}
                )
            except httpx.TimeoutException as e:
                logger.error(f"VBank auth timeout: {e}")
                raise VBankAPIError(
                    "VBank authentication timeout. Please try again.",
                    status_code=504,
                    details={"error": str(e)}
                )
            except httpx.RequestError as e:
                logger.error(f"VBank auth request error: {e}")
                raise VBankAPIError(
                    "Failed to connect to VBank API",
                    status_code=503,
                    details={"error": str(e)}
                )
            except Exception as e:
                logger.error(f"Unexpected VBank auth error: {e}")
                raise VBankAPIError(
                    "Unexpected error during VBank authentication",
                    details={"error": str(e)}
                )


class VBankClient:
    def __init__(self, base_url: str, client_id: str, client_secret: str, bank_code: str):
        self.base_url = base_url.rstrip("/")
        self._auth = VBankAuth(base_url, client_id, client_secret, bank_code)
        self._http = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def _headers(self) -> Dict[str, str]:
        token = await self._auth.token(self._http)
        return {"Authorization": f"Bearer {token}"}

    async def get_accounts(self) -> Dict[str, Any]:
        try:
            # примерный путь — в sandbox обычно /accounts или /client/accounts
            # если у них другой — поправим одну строку тут, без касания остального кода
            r = await self._http.get("/accounts", headers=await self._headers())
            r.raise_for_status()
            return r.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"VBank get_accounts HTTP error: {e.response.status_code}")
            raise VBankAPIError(
                f"Failed to fetch accounts from VBank: {e.response.status_code}",
                status_code=e.response.status_code,
                details={"response": e.response.text}
            )
        except httpx.TimeoutException as e:
            logger.error(f"VBank get_accounts timeout: {e}")
            raise VBankAPIError(
                "VBank API timeout while fetching accounts",
                status_code=504
            )
        except Exception as e:
            logger.error(f"VBank get_accounts error: {e}")
            raise VBankAPIError(f"Error fetching accounts: {str(e)}")

    async def get_transactions(self, account_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        try:
            params = {}
            if date_from: params["dateFrom"] = date_from
            if date_to: params["dateTo"] = date_to
            # частый профиль: /accounts/{id}/transactions
            r = await self._http.get(f"/accounts/{account_id}/transactions", params=params, headers=await self._headers())
            r.raise_for_status()
            return r.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"VBank get_transactions HTTP error: {e.response.status_code}")
            raise VBankAPIError(
                f"Failed to fetch transactions from VBank: {e.response.status_code}",
                status_code=e.response.status_code,
                details={"response": e.response.text}
            )
        except httpx.TimeoutException as e:
            logger.error(f"VBank get_transactions timeout: {e}")
            raise VBankAPIError(
                "VBank API timeout while fetching transactions",
                status_code=504
            )
        except Exception as e:
            logger.error(f"VBank get_transactions error: {e}")
            raise VBankAPIError(f"Error fetching transactions: {str(e)}")

    async def aclose(self):
        await self._http.aclose()


class MockVBankClient:
    """Mock client for development when credentials are missing"""
    def __init__(self):
        pass

    async def get_accounts(self) -> Dict[str, Any]:
        # Return dummy accounts
        return {
            "accounts": [
                {
                    "id": "mock_acc_1",
                    "name": "Mock Checking Account",
                    "currency": "RUB",
                    "balance": 150000.00,
                    "product": "Debit Card",
                    "status": "active"
                },
                {
                    "id": "mock_acc_2",
                    "name": "Mock Savings",
                    "currency": "RUB",
                    "balance": 500000.00,
                    "product": "Savings",
                    "status": "active"
                }
            ]
        }

    async def get_transactions(self, account_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        # Return dummy transactions
        return {
            "transactions": [
                {
                    "id": "mock_tx_1",
                    "amount": -1500.00,
                    "currency": "RUB",
                    "bookingDate": "2023-10-25",
                    "description": "Grocery Store",
                    "category": "Food",
                    "status": "posted"
                },
                {
                    "id": "mock_tx_2",
                    "amount": -500.00,
                    "currency": "RUB",
                    "bookingDate": "2023-10-26",
                    "description": "Coffee Shop",
                    "category": "Dining",
                    "status": "posted"
                },
                {
                    "id": "mock_tx_3",
                    "amount": 50000.00,
                    "currency": "RUB",
                    "bookingDate": "2023-10-20",
                    "description": "Salary",
                    "category": "Income",
                    "status": "posted"
                }
            ]
        }
    
    async def aclose(self):
        pass


# Фабрика-одиночка
_vbank_singleton: Optional[Any] = None

def get_vbank_client() -> Any:
    global _vbank_singleton
    if _vbank_singleton is None:
        if not settings.VBANK_CLIENT_ID or not settings.VBANK_CLIENT_SECRET:
            _vbank_singleton = MockVBankClient()
        else:
            _vbank_singleton = VBankClient(
                base_url=settings.VBANK_BASE_URL,
                client_id=settings.VBANK_CLIENT_ID,
                client_secret=settings.VBANK_CLIENT_SECRET,
                bank_code=settings.VBANK_BANK_CODE,
            )
    return _vbank_singleton
