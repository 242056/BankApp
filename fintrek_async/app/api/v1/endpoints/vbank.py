from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from fintrek_async.app.api.v1.deps import get_current_user
from fintrek_async.app.db.session import get_db
from fintrek_async.app.services.vbank_import import VBankImportService

router = APIRouter(prefix="/vbank", tags=["vbank"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/sync-accounts")
@limiter.limit("10/minute")  # Ограничение для дорогих операций с внешним API
async def sync_accounts(
    request: Request,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = VBankImportService()
    await svc.fetch_accounts(db, user_id=current_user.id)
    await db.commit()
    return {"status": "ok"}

@router.post("/sync-transactions")
@limiter.limit("10/minute")  # Ограничение для дорогих операций с внешним API
async def sync_transactions(
    request: Request,
    account_id: str = Query(..., description="external account id из VBank"),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = VBankImportService()
    await svc.fetch_transactions(db, user_id=current_user.id, account_id=account_id, date_from=date_from, date_to=date_to)
    await db.commit()
    return {"status": "ok"}
