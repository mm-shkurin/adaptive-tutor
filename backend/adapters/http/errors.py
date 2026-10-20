from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from domain.account.name import NameNotAllowed
from domain.account.photo import PhotoNotAllowed, PhotoTooLarge
from usecase.account.errors import StoreUnavailable, Unauthorized

_UNAUTHORIZED = {"code": "unauthorized", "message": "Credentials are not valid"}
_INVALID = {"code": "invalid_request", "message": "The request is not valid"}
_NAME = {"code": "invalid_name", "message": "Name is not allowed"}
_PHOTO = {"code": "invalid_photo", "message": "Photo is not allowed"}
_LARGE = {"code": "photo_too_large", "message": "Photo is too large"}
_STORE = {"code": "unavailable", "message": "The account store is unreachable"}
_FINISHED = {"code": "unavailable", "message": "The request could not be finished"}


def register_errors(app: FastAPI) -> None:
    app.add_exception_handler(Unauthorized, _status(401, _UNAUTHORIZED))
    app.add_exception_handler(NameNotAllowed, _status(422, _NAME))
    app.add_exception_handler(PhotoNotAllowed, _status(422, _PHOTO))
    app.add_exception_handler(PhotoTooLarge, _status(413, _LARGE))
    app.add_exception_handler(StoreUnavailable, _status(503, _STORE))
    app.add_exception_handler(RequestValidationError, _status(422, _INVALID))
    app.add_exception_handler(Exception, _status(500, _FINISHED))


def _status(status: int, body: dict):
    async def handler(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content=body)

    return handler
