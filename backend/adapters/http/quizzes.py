from typing import Any
from uuid import UUID

from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from adapters.http.auth import _bearer
from domain.quiz.errors import InvalidIdempotencyKey
from usecase.account.errors import StoreUnavailable as AccountStoreUnavailable
from usecase.account.errors import Unauthorized
from usecase.quiz.errors import QuizNotFound

router = APIRouter()

_KEY_LIMIT = 128


class CreateQuizBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: UUID
    topic: Any = None
    question_count: Any = 5


class AnswerQuizBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    choice_id: str


@router.get("")
async def list_quizzes(request: Request):
    account = await _caller(request)
    quizzes = await request.app.state.ctx.list_quizzes.list(account.id)
    return {"quizzes": [quiz.card() for quiz in quizzes]}


@router.post("", status_code=201)
async def create_quiz(
    body: CreateQuizBody,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    key = _idempotency_key(idempotency_key)
    account = await _caller(request)
    quiz = await request.app.state.ctx.create_quiz.create(
        account.id, body.document_id, body.topic, body.question_count, key
    )
    return JSONResponse(status_code=201, content=quiz.detail())


@router.get("/{id}")
async def get_quiz(id: UUID, request: Request):
    account = await _caller(request)
    quiz = await request.app.state.ctx.get_quiz.open(account.id, id)
    return quiz.detail()


@router.post("/{id}/answers")
async def answer_quiz(id: UUID, body: AnswerQuizBody, request: Request):
    account = await _caller(request)
    quiz = await request.app.state.ctx.answer_quiz.answer(account.id, id, body.choice_id)
    return quiz.detail()


@router.post("/{id}/advance")
async def advance_quiz(id: UUID, request: Request):
    account = await _caller(request)
    quiz = await request.app.state.ctx.advance_quiz.advance(account.id, id)
    return quiz.detail()


@router.post("/{id}/retries")
async def retry_quiz(id: UUID, request: Request):
    account = await _caller(request)
    quiz = await request.app.state.ctx.retry_quiz.retry(account.id, id)
    return quiz.detail()


def _idempotency_key(raw: str | None) -> str:
    if not isinstance(raw, str) or raw == "" or len(raw) > _KEY_LIMIT:
        raise InvalidIdempotencyKey()
    return raw


async def _caller(request: Request):
    try:
        return await request.app.state.ctx.session.caller(_bearer(request))
    except (Unauthorized, AccountStoreUnavailable) as error:
        raise QuizNotFound() from error
