import asyncio
import json
from collections.abc import AsyncIterator
from urllib.parse import unquote
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.datastructures import UploadFile as FormUpload

from adapters.http.auth import _bearer
from adapters.pdfreader.upload_check import reject_unreadable_pdf
from domain.document.document import Document
from domain.document.file_name import DocumentNameError, canonical_name
from usecase.account.errors import Unauthorized
from usecase.document.errors import DocumentNotFound, InvalidDocument

router = APIRouter()

_MIN_BYTES = 1_048_576
_MAX_BYTES = 52_428_800
_CHUNK = 64 * 1024
_KEEPALIVE_SECONDS = 15.0
_NOT_FOUND = {"code": "document_not_found", "message": "Document was not found"}
_NAME_MESSAGES = {
    "name_missing": "File name is missing",
    "name_too_long": "File name is too long",
}
_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@router.get("")
async def list_documents(
    request: Request,
    page: int = Query(1, ge=1),
    after: UUID | None = Query(None),
):
    account = await _caller(request)
    documents, has_next = await request.app.state.ctx.list_documents.list(
        account.id, page, after
    )
    return {"documents": [_json(document) for document in documents], "has_next": has_next}


@router.post("", status_code=201)
async def upload_document(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=1, max_length=255),
):
    account = await _caller(request)
    upload = await _upload_part(request)
    name = _name(upload.filename)
    content = await _read_pdf(upload)
    accepted = await request.app.state.ctx.submit_document.submit(
        account.id, name, content, idempotency_key
    )
    if accepted.created:
        request.app.state.ctx.schedule_indexing()
    return JSONResponse(
        status_code=201 if accepted.created else 200,
        content=_json(accepted.document),
    )


@router.get("/status-events")
async def document_status_events(request: Request):
    account = await _caller(request)
    hub = request.app.state.ctx.status_hub
    queue = hub.subscribe(account.id)
    documents, _ = await request.app.state.ctx.list_documents.list(account.id, 1, None)

    async def events() -> AsyncIterator[str]:
        try:
            yield ": connected\n\n"
            for document in documents:
                yield _sse_event(document)
            while True:
                if await request.is_disconnected():
                    break
                try:
                    document = await asyncio.wait_for(queue.get(), timeout=_KEEPALIVE_SECONDS)
                except TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                yield _sse_event(document)
        finally:
            hub.unsubscribe(account.id, queue)

    return StreamingResponse(events(), media_type="text/event-stream", headers=_SSE_HEADERS)


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


async def _upload_part(request: Request) -> UploadFile:
    try:
        form = await request.form()
    except Exception as error:
        raise InvalidDocument("file_missing", "File is missing") from error
    if "file" not in form:
        raise InvalidDocument("file_missing", "File is missing")
    part = form["file"]
    if not isinstance(part, FormUpload):
        # Empty filename is parsed as a plain field, not an upload.
        raise InvalidDocument("name_missing", "File name is missing")
    return part


def _name(filename: str | None) -> str:
    if filename is None:
        raise InvalidDocument("name_missing", "File name is missing")
    try:
        return canonical_name(unquote(filename))
    except DocumentNameError as error:
        raise InvalidDocument(error.code, _NAME_MESSAGES[error.code]) from error


async def _read_pdf(upload: UploadFile) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while chunk := await upload.read(_CHUNK):
        size += len(chunk)
        if size > _MAX_BYTES:
            raise InvalidDocument("file_too_large", "File is too large")
        chunks.append(chunk)
    return _require_acceptable_pdf(b"".join(chunks))


def _require_acceptable_pdf(content: bytes) -> bytes:
    if len(content) < _MIN_BYTES:
        raise InvalidDocument("file_too_small", "File is too small")
    if not content.startswith(b"%PDF"):
        raise InvalidDocument("invalid_pdf", "File is not a PDF")
    reject_unreadable_pdf(content)
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


def _sse_event(document: Document) -> str:
    return f"event: document-status\ndata: {json.dumps(_json(document))}\n\n"
