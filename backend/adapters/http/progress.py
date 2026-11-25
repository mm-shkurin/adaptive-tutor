from uuid import UUID

from fastapi import APIRouter, Query, Request

from adapters.http.auth import _bearer
from usecase.account.errors import StoreUnavailable as AccountStoreUnavailable
from usecase.account.errors import Unauthorized
from usecase.presentation.get_progress import GetProgress, ProgressNotFound

router = APIRouter()


@router.get("")
async def read_progress(request: Request, material: UUID | None = Query(default=None)):
    account = await _caller(request)
    body = await request.app.state.ctx.get_progress.read(account.id, material)
    return body


async def _caller(request: Request):
    try:
        return await request.app.state.ctx.session.caller(_bearer(request))
    except (Unauthorized, AccountStoreUnavailable) as error:
        raise ProgressNotFound() from error