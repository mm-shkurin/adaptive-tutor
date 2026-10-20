from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import Response

router = APIRouter()


@router.get("/avatars/{key}")
async def read_avatar(key: UUID, request: Request):
    found = await request.app.state.ctx.accounts.read_avatar(key)
    if found is None:
        return Response(
            status_code=404,
            content='{"code":"not_found","message":"Photo was not found"}',
            media_type="application/json",
        )
    body, content_type = found
    return Response(content=body, media_type=content_type)
