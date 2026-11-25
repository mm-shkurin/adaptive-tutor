from uuid import UUID

from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict

from adapters.http.auth import _bearer
from usecase.account.errors import StoreUnavailable as AccountStoreUnavailable
from usecase.account.errors import Unauthorized
from usecase.presentation.errors import PresentationNotFound

router = APIRouter()
_KEY_LIMIT = 255


class CreateBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str | None = None


class SlideText(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: UUID
    text: str


class PatchBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str | None = None
    slide_order: list[UUID] | None = None
    slides: list[SlideText] | None = None


@router.post("", status_code=201)
async def create_presentation(body: CreateBody, request: Request):
    account = await _caller(request)
    item = await request.app.state.ctx.create_presentation.create(account.id, body.title)
    return JSONResponse(status_code=201, content=item.json())


@router.get("/{id}")
async def get_presentation(id: UUID, request: Request):
    account = await _caller(request)
    item = await request.app.state.ctx.get_presentation.open(account.id, id)
    return item.json()


@router.patch("/{id}")
async def patch_presentation(id: UUID, body: PatchBody, request: Request):
    account = await _caller(request)
    item = await request.app.state.ctx.patch_presentation.patch(account.id, id, body.model_dump(exclude_none=True))
    return item.json()


@router.delete("/{id}", status_code=204)
async def delete_presentation(id: UUID, request: Request):
    account = await _caller(request)
    await request.app.state.ctx.delete_presentation.delete(account.id, id)
    return Response(status_code=204)


@router.post("/{id}/slides")
async def add_slides(
    id: UUID,
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=1, max_length=_KEY_LIMIT),
):
    account = await _caller(request)
    uploads = (await request.form()).getlist("images")
    payload = tuple([await upload.read() for upload in uploads])
    item = await request.app.state.ctx.add_slides.images(account.id, id, idempotency_key, payload)
    return item.json()


@router.delete("/{id}/slides/{slide_id}")
async def delete_slide(id: UUID, slide_id: UUID, request: Request):
    account = await _caller(request)
    item = await request.app.state.ctx.patch_presentation.delete_slide(account.id, id, slide_id)
    return item.json()


@router.post("/{id}/index")
async def index_presentation(
    id: UUID,
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=1, max_length=_KEY_LIMIT),
):
    account = await _caller(request)
    item, replayed = await request.app.state.ctx.index_presentation.index(account.id, id, idempotency_key)
    status = 200 if replayed else 202
    return JSONResponse(status_code=status, content=item.json())


async def _caller(request: Request):
    try:
        return await request.app.state.ctx.session.caller(_bearer(request))
    except (Unauthorized, AccountStoreUnavailable) as error:
        raise PresentationNotFound() from error