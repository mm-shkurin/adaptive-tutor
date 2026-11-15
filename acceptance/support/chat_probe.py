from uuid import UUID

from fastapi import Body, FastAPI, Request
from fastapi.responses import Response

from domain.chat.source import Source


def register_chat_probe(app: FastAPI, search, tutor, intake, vectors=None) -> None:
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

    @app.post("/acceptance/tutor/fail", status_code=204)
    async def fail_tutor(request: Request):
        await document_caller(request)
        tutor.fail()
        return Response(status_code=204)

    @app.post("/acceptance/tutor/hang", status_code=204)
    async def hang_tutor(request: Request):
        await document_caller(request)
        tutor.hang()
        return Response(status_code=204)

    @app.post("/acceptance/search/advance-on-match", status_code=204)
    async def advance_on_match(request: Request, body: dict = Body(...)):
        await document_caller(request)
        search.advance_clock_on_match(int(body["offset_ms"]))
        return Response(status_code=204)

    @app.get("/acceptance/tutor/calls")
    async def tutor_calls(request: Request):
        await document_caller(request)
        return {"calls": [call.json() for call in tutor.calls], "finished": tutor.finished}

    @app.post("/acceptance/vectors/interleave", status_code=204)
    async def arm_interleave(request: Request):
        await document_caller(request)
        from support.vector_latch import VectorLatch

        assert vectors is not None
        vectors.arm_interleave(VectorLatch())
        return Response(status_code=204)

    @app.post("/acceptance/chats/{chat_id}/interleave-open")
    async def interleave_open(chat_id: UUID, request: Request):
        import asyncio

        account = await document_caller(request)
        get_chat = request.app.state.ctx.get_chat

        async def once():
            chat = await get_chat.open(account.id, chat_id)
            return {"askable": chat.askable(), "notice": chat.notice()}

        first, second = await asyncio.gather(once(), once())
        return {"opens": [first, second]}

    @app.post("/acceptance/vectors/write-empty", status_code=204)
    async def write_empty(request: Request):
        await document_caller(request)
        assert vectors is not None
        from uuid import uuid4

        await vectors.write(uuid4(), ())
        return Response(status_code=204)
