from uuid import UUID

from fastapi import Body, FastAPI, Request
from fastapi.responses import Response

from domain.chat.source import Source


def register_chat_probe(app: FastAPI, search, tutor, intake) -> None:
    from adapters.http.documents import _caller as document_caller

    @app.post("/acceptance/documents/{document_id}/search-pieces", status_code=204)
    async def seed_search(document_id: UUID, request: Request, body: dict = Body(...)):
        account = await document_caller(request)
        row = intake.rows.get(document_id)
        if row is None or row[0] != account.id:
            from usecase.document.errors import DocumentNotFound

            raise DocumentNotFound()
        search.seed(
            document_id,
            tuple(Source(page=item["page"], text=item["text"]) for item in body["pieces"]),
        )
        return Response(status_code=204)

    @app.post("/acceptance/tutor/script", status_code=204)
    async def script_tutor(request: Request, body: dict = Body(...)):
        await document_caller(request)
        tutor.script(body["text"])
        return Response(status_code=204)

    @app.get("/acceptance/tutor/calls")
    async def tutor_calls(request: Request):
        await document_caller(request)
        return {"calls": [call.json() for call in tutor.calls]}
