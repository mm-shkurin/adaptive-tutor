from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from adapters.http.auth import _bearer
from domain.chat.chat import Chat
from usecase.account.errors import Unauthorized
from usecase.chat.errors import ChatNotFound

router = APIRouter()


class CreateChatBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: UUID | None = None


@router.get("")
async def list_chats(request: Request):
    account = await _caller(request)
    chats = await request.app.state.ctx.list_chats.list(account.id)
    return {"chats": [_summary(chat) for chat in chats]}


@router.post("", status_code=201)
async def create_chat(body: CreateChatBody, request: Request):
    account = await _caller(request)
    chat = await request.app.state.ctx.create_chat.start(account.id, body.document_id)
    return JSONResponse(status_code=201, content=_chat(chat))


async def _caller(request: Request):
    try:
        return await request.app.state.ctx.session.caller(_bearer(request))
    except Unauthorized as error:
        raise ChatNotFound() from error


def _summary(chat: Chat) -> dict:
    return {
        "id": str(chat.id),
        "document_id": str(chat.document_id),
        "document_name": chat.document_name,
        "preview": chat.preview(),
    }


def _chat(chat: Chat) -> dict:
    return {
        "id": str(chat.id),
        "document_id": str(chat.document_id),
        "document_name": chat.document_name,
        "askable": chat.askable(),
        "notice": chat.notice(),
        "lines": list(chat.lines),
    }
