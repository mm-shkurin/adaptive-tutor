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

    @app.post("/acceptance/search/fail", status_code=204)
    async def fail_search(request: Request):
        await document_caller(request)
        search.fail()
        return Response(status_code=204)

    @app.post("/acceptance/model-key/clear", status_code=204)
    async def clear_model_key(request: Request):
        await document_caller(request)
        tutor.api_key = ""
        return Response(status_code=204)

    @app.post("/acceptance/model-key/set", status_code=204)
    async def set_model_key(request: Request, body: dict = Body(...)):
        await document_caller(request)
        tutor.api_key = str(body.get("key") or "")
        return Response(status_code=204)

    @app.post("/acceptance/tutor/hang", status_code=204)
    async def hang_tutor(request: Request):
        await document_caller(request)
        tutor.hang()
        return Response(status_code=204)

    @app.post("/acceptance/tutor/hold", status_code=204)
    async def hold_tutor(request: Request):
        await document_caller(request)
        from support.tutor_hold import TutorHold

        tutor.hold(TutorHold())
        return Response(status_code=204)

    @app.post("/acceptance/chat/latency", status_code=204)
    async def set_chat_latency(request: Request, body: dict = Body(...)):
        from datetime import timedelta

        await document_caller(request)
        request.app.state.ctx.send_message.latency = timedelta(milliseconds=int(body["ms"]))
        return Response(status_code=204)

    @app.post("/acceptance/tutor/release", status_code=204)
    async def release_tutor(request: Request):
        await document_caller(request)
        hold = tutor._hold
        if hold is not None:
            hold.release()
        return Response(status_code=204)

    @app.post("/acceptance/tutor/hold-each", status_code=204)
    async def hold_each_tutor(request: Request, body: dict | None = Body(None)):
        await document_caller(request)
        payload = body or {}
        texts = tuple(payload.get("texts") or ())
        tutor.hold_each(texts)
        return Response(status_code=204)

    @app.get("/acceptance/tutor/holds")
    async def tutor_holds(request: Request):
        await document_caller(request)
        entered = sum(1 for hold in tutor._each_holds if hold._entered.is_set())
        return {"entered": entered, "total": len(tutor._each_holds)}

    @app.post("/acceptance/tutor/release-call", status_code=204)
    async def release_tutor_call(request: Request, body: dict = Body(...)):
        await document_caller(request)
        tutor.release_call(int(body["index"]))
        return Response(status_code=204)

    @app.post("/acceptance/chats/{chat_id}/reply-after-switch")
    async def reply_after_switch(chat_id: UUID, request: Request, body: dict = Body(...)):
        import asyncio

        from adapters.http.chats import _attempt, _chat
        from usecase.chat.outgoing import Outgoing

        account = await document_caller(request)
        hold = tutor._hold
        assert hold is not None
        outgoing = Outgoing.from_payload(
            {"text": body["text"], "model": body["model"], "mode": body["mode"]}
        )
        send = request.app.state.ctx.send_message
        open_chat = request.app.state.ctx.open_chat
        get_chat = request.app.state.ctx.get_chat

        task = asyncio.create_task(
            send.send(account.id, chat_id, outgoing, body["key"])
        )
        await hold.until_entered()
        opened = await open_chat.open(account.id, UUID(body["document_id"]))
        hold.release()
        attempt = await task
        left = await get_chat.open(account.id, chat_id)
        return {
            "sent": _attempt(attempt),
            "opened": _chat(opened.chat),
            "left": _chat(left),
        }

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

    @app.post("/acceptance/chats/store-reads/reset", status_code=204)
    async def reset_store_reads(request: Request):
        await document_caller(request)
        chats = request.app.state.ctx.list_chats.chats
        chats.reset_reads()
        return Response(status_code=204)

    @app.get("/acceptance/chats/store-reads")
    async def store_reads(request: Request):
        await document_caller(request)
        chats = request.app.state.ctx.list_chats.chats
        return {"reads": chats.reads}

    @app.post("/acceptance/session-store/fail", status_code=204)
    async def fail_session_store(request: Request):
        await document_caller(request)
        accounts = request.app.state.accounts
        accounts.dead = True
        return Response(status_code=204)

    @app.post("/acceptance/session-store/recover", status_code=204)
    async def recover_session_store(request: Request):
        accounts = request.app.state.accounts
        accounts.dead = False
        return Response(status_code=204)

    @app.post("/acceptance/chat-store/fail", status_code=204)
    async def fail_chat_store(request: Request):
        await document_caller(request)
        request.app.state.ctx.list_chats.chats.dead = True
        return Response(status_code=204)

    @app.post("/acceptance/chat-store/recover", status_code=204)
    async def recover_chat_store(request: Request):
        request.app.state.ctx.list_chats.chats.dead = False
        return Response(status_code=204)

    @app.post("/acceptance/search/recover", status_code=204)
    async def recover_search(request: Request):
        search.clear_fail()
        return Response(status_code=204)

    @app.get("/acceptance/store-connections")
    async def store_connections(request: Request):
        await document_caller(request)
        return {
            "chat_store": request.app.state.ctx.list_chats.chats.live,
            "search_store": search.live,
            "model": tutor.live,
            "embeddings": 0 if vectors is None else vectors.embeddings_live,
        }

    @app.post("/acceptance/chats/interleave-thread", status_code=204)
    async def arm_thread_interleave(request: Request):
        await document_caller(request)
        from support.vector_latch import VectorLatch

        request.app.state.ctx.list_chats.chats.arm_thread_interleave(VectorLatch())
        return Response(status_code=204)

    @app.post("/acceptance/chats/interleave-attempt", status_code=204)
    async def arm_attempt_interleave(request: Request):
        await document_caller(request)
        from support.vector_latch import VectorLatch

        request.app.state.ctx.list_chats.chats.arm_attempt_interleave(VectorLatch())
        return Response(status_code=204)

    @app.post("/acceptance/chats/{chat_id}/interleave-sends")
    async def interleave_sends(chat_id: UUID, request: Request, body: dict = Body(...)):
        import asyncio

        from adapters.http.chats import _attempt, _chat
        from usecase.chat.outgoing import Outgoing

        account = await document_caller(request)
        send = request.app.state.ctx.send_message
        get_chat = request.app.state.ctx.get_chat

        async def once(item: dict):
            if "payload" in item:
                outgoing = Outgoing.from_payload(item["payload"])
            else:
                outgoing = Outgoing.from_payload(
                    {"text": item["text"], "model": item["model"], "mode": item["mode"]}
                )
            return await send.send(account.id, chat_id, outgoing, item["key"])

        results = await asyncio.gather(*(once(item) for item in body["attempts"]))
        opened = await get_chat.open(account.id, chat_id)
        return {
            "sends": [_attempt(result) for result in results],
            "thread": _chat(opened),
        }
