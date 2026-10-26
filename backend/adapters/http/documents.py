from uuid import UUID

from fastapi import APIRouter, File, Header, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from adapters.http.auth import _bearer
from domain.document.document import Document
from usecase.account.errors import Unauthorized
from usecase.document.errors import DocumentNotFound, InvalidDocument

router = APIRouter()

_MIN_BYTES = 1_048_576
_MAX_BYTES = 52_428_800
_NAME_LIMIT = 255
_CHUNK = 64 * 1024
_NOT_FOUND = {"code": "document_not_found", "message": "Document was not found"}


@router.get("")
async def list_documents(request: Request, page: int = Query(1, ge=1)):
    account = await _caller(request)
    documents, has_next = await request.app.state.ctx.list_documents.list(account.id, page)
    return {"documents": [_json(document) for document in documents], "has_next": has_next}


@router.post("", status_code=201)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=1, max_length=255),
):
    account = await _caller(request)
    name = _name(file.filename)
    content = await _read_pdf(file)
    accepted = await request.app.state.ctx.submit_document.submit(
        account.id, name, content, idempotency_key
    )
    if accepted.created:
        request.app.state.ctx.schedule_indexing()
    return JSONResponse(
        status_code=201 if accepted.created else 200,
        content=_json(accepted.document),
    )


@router.get("/{document_id}")
async def get_document(document_id: UUID, request: Request):
    account = await _caller(request)
    try:
        document = await request.app.state.ctx.read_document.read(account.id, document_id)
    except KeyError as error:
        raise DocumentNotFound() from error
    return _json(document)


async def _caller(request: Request):
    try:
        return await request.app.state.ctx.session.caller(_bearer(request))
    except Unauthorized as error:
        raise DocumentNotFound() from error


def _name(filename: str | None) -> str:
    if filename is None or filename.strip() == "":
        raise InvalidDocument("name_missing", "File name is missing")
    if len(filename) > _NAME_LIMIT:
        raise InvalidDocument("name_too_long", "File name is too long")
    return filename


async def _read_pdf(upload: UploadFile) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while chunk := await upload.read(_CHUNK):
        size += len(chunk)
        if size > _MAX_BYTES:
            raise InvalidDocument("file_too_large", "File is too large")
        chunks.append(chunk)
    content = b"".join(chunks)
    if len(content) < _MIN_BYTES:
        raise InvalidDocument("file_too_small", "File is too small")
    if not content.startswith(b"%PDF"):
        raise InvalidDocument("invalid_pdf", "File is not a PDF")
    return content


def _json(document: Document) -> dict:
    return {
        "id": str(document.id),
        "name": document.name,
        "size_bytes": document.size_bytes,
        "page_count": document.page_count,
        "piece_count": document.piece_count,
        "status": document.status,
        "error": document.error,
    }
