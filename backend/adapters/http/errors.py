from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from domain.account.name import NameNotAllowed
from domain.account.photo import PhotoNotAllowed, PhotoTooLarge
from domain.chat.chat import DocumentNotReady, NotAskable
from domain.chat.learning import EmptyQuestion, ModeNotListed, ModelNotListed
from usecase.account.errors import StoreUnavailable as AccountStoreUnavailable
from usecase.account.errors import Unauthorized
from usecase.chat.errors import ChatNotFound
from usecase.chat.errors import NoReadyDocument
from usecase.chat.errors import StoreUnavailable as ChatStoreUnavailable
from usecase.document.errors import DocumentNotFound, InvalidDocument, RateLimited, RateUnavailable
from usecase.document.errors import StoreUnavailable as DocumentStoreUnavailable

_UNAUTHORIZED = {"code": "unauthorized", "message": "Credentials are not valid"}
_INVALID = {"code": "invalid_request", "message": "The request is not valid"}
_NAME = {"code": "invalid_name", "message": "Name is not allowed"}
_PHOTO = {"code": "invalid_photo", "message": "Photo is not allowed"}
_LARGE = {"code": "photo_too_large", "message": "Photo is too large"}
_STORE = {"code": "unavailable", "message": "The account store is unreachable"}
_FINISHED = {"code": "unavailable", "message": "The request could not be finished"}
_DOCUMENT_MISSING = {"code": "document_not_found", "message": "Document was not found"}
_CHAT_MISSING = {"code": "chat_not_found", "message": "Chat was not found"}
_NOT_READY = {"code": "document_not_ready", "message": "Document is not ready"}
_NO_READY = {"code": "no_ready_document", "message": "No ready document"}
_CHAT_STORE = {"code": "unavailable", "message": "The chat store is unreachable"}
_EMPTY = {"code": "empty_message", "message": "Message is empty"}
_MODEL = {"code": "invalid_model", "message": "Model is not allowed"}
_MODE = {"code": "invalid_mode", "message": "Mode is not allowed"}
_NOT_ASKABLE = {"code": "not_askable", "message": "Material cannot be asked yet"}


def register_errors(app: FastAPI) -> None:
    app.add_exception_handler(Unauthorized, _status(401, _UNAUTHORIZED))
    app.add_exception_handler(DocumentNotFound, _status(404, _DOCUMENT_MISSING))
    app.add_exception_handler(ChatNotFound, _status(404, _CHAT_MISSING))
    app.add_exception_handler(DocumentNotReady, _status(400, _NOT_READY))
    app.add_exception_handler(NoReadyDocument, _status(400, _NO_READY))
    app.add_exception_handler(ChatStoreUnavailable, _status(503, _CHAT_STORE))
    app.add_exception_handler(EmptyQuestion, _status(400, _EMPTY))
    app.add_exception_handler(ModelNotListed, _status(400, _MODEL))
    app.add_exception_handler(ModeNotListed, _status(400, _MODE))
    app.add_exception_handler(NotAskable, _status(409, _NOT_ASKABLE))
    app.add_exception_handler(InvalidDocument, _invalid_document)
    app.add_exception_handler(RateLimited, _rate_refusal)
    app.add_exception_handler(RateUnavailable, _rate_refusal)
    app.add_exception_handler(NameNotAllowed, _status(422, _NAME))
    app.add_exception_handler(PhotoNotAllowed, _status(422, _PHOTO))
    app.add_exception_handler(PhotoTooLarge, _status(413, _LARGE))
    app.add_exception_handler(AccountStoreUnavailable, _status(503, _STORE))
    app.add_exception_handler(DocumentStoreUnavailable, _status(503, _STORE))
    app.add_exception_handler(RequestValidationError, _status(422, _INVALID))
    app.add_exception_handler(Exception, _status(500, _FINISHED))


def _status(status: int, body: dict):
    async def handler(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content=body)

    return handler


async def _invalid_document(_request: Request, exc: InvalidDocument) -> JSONResponse:
    return JSONResponse(status_code=400, content={"code": exc.code, "message": exc.message})


async def _rate_refusal(_request: Request, exc: RateLimited | RateUnavailable) -> JSONResponse:
    return JSONResponse(status_code=429, content={"code": exc.code, "message": exc.message})
