import asyncio
import socket
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from uuid import UUID
import httpx
import uvicorn
from fastapi import Body, FastAPI, Request
from fastapi.responses import JSONResponse

from adapters.memory.account_store import MemoryAccountStore
from adapters.memory.document_intake import MemoryDocumentIntake
from adapters.memory.file_store import MemoryFileStore
from adapters.memory.oauth_store import MemoryOAuthStore
from clients.application.probe_piece_index import ProbePieceIndex
from clients.application.probe_submit_document import ProbeSubmitDocument
from adapters.memory.revocations import MemoryRevocations
from adapters.memory.upload_rate_limit import MemoryUploadRateLimit
from adapters.pdfreader.pdf_reader import PyPdfReader
from clients.application.probe_gated_pdf_reader import ProbeGatedPdfReader
from adapters.tokens.jwt_tokens import JwtTokens
from domain.document.document import InvalidStatusTransition
from application.context import AppContext, RuntimeConfig
from application.main import create_app
from clients.application.index_probe import IndexProbe
from clients.application.session_client import ScriptedProvider
from usecase.account.profile import ProfileService
from usecase.account.session import SessionService
from usecase.account.sign_in import SignIn
from clients.application.probe_index_documents import ProbeIndexDocuments
from usecase.document.list_documents import ListDocuments
from usecase.document.read_document import ReadDocument
from usecase.document.search_documents import SearchDocuments
from usecase.document.submit_document import SubmitDocument
from support.disclosure_constants import DISCLOSURE_KNOWN_SECRET
from support.log_capture import LogCapture


def _state_ttl() -> timedelta:
    return timedelta(seconds=600)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class _Clock:
    def __init__(self):
        self.moment = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)

    def now(self):
        return self.moment

    def advance(self, seconds: int) -> None:
        self.moment += timedelta(seconds=seconds)


class AcceptanceServer:
    def __init__(self):
        self.provider = ScriptedProvider()
        self.probe = IndexProbe()
        self.clock = _Clock()
        self.rates = MemoryUploadRateLimit(self.clock)
        self.logs = LogCapture()
        port = _free_port()
        self.base_url = f"http://127.0.0.1:{port}"
        self._indexing = asyncio.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._ctx: AppContext | None = None
        self.probe.bind_second_index_run(self._run_second_indexing_sync)
        self.probe.bind_dual_claim_race(self._run_dual_claim_race_sync)
        self._serve(port)

    def _context(self) -> AppContext:
        store = MemoryAccountStore()
        tokens = JwtTokens(
            DISCLOSURE_KNOWN_SECRET, "b" * 32, timedelta(minutes=60), timedelta(days=30)
        )
        bodies: dict[UUID, bytes] = {}
        intake = MemoryDocumentIntake(bodies, self.probe, now=self.clock.now)
        files = MemoryFileStore(bodies, self.probe)
        pieces = ProbePieceIndex(self.probe)
        self.probe.attach_intake(intake)
        self.probe.attach_pieces(pieces)
        self._intake = intake
        self._pieces = pieces
        reader = ProbeGatedPdfReader(PyPdfReader(), self.probe)
        return AppContext(
            RuntimeConfig(_state_ttl(), ("http://localhost:5173",)),
            self._sign_in(store, tokens),
            SessionService(store, tokens, MemoryRevocations()),
            ProfileService(store, self.base_url),
            store,
            ProbeSubmitDocument(intake, self.rates, self.probe),
            ReadDocument(intake),
            ListDocuments(intake),
            ProbeIndexDocuments(intake, files, reader, pieces, self.probe, self.clock),
            self._indexing,
        )

    def _sign_in(self, store: MemoryAccountStore, tokens: JwtTokens) -> SignIn:
        return SignIn(
            self.provider,
            MemoryOAuthStore(),
            store,
            tokens,
            self.clock,
            _state_ttl(),
            timedelta(seconds=120),
            "http://localhost:5173/auth/callback",
        )

    def _serve(self, port: int) -> None:
        ctx = self._context()
        self._ctx = ctx

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            self._loop = asyncio.get_running_loop()
            task = asyncio.create_task(self._index_loop(ctx))
            app.state.indexing_task = task
            yield
            task.cancel()

        app = create_app(ctx)
        app.router.lifespan_context = lifespan
        app.state.index_probe = self.probe
        search = SearchDocuments(self._intake, self._pieces)

        from adapters.http.documents import _caller as document_caller

        @app.get("/acceptance/documents/{document_id}/searchable-pieces")
        async def searchable_pieces(document_id: UUID, request: Request):
            account = await document_caller(request)
            found = await search.pieces_for(account.id, document_id)
            return {"pieces": list(found)}

        @app.post("/acceptance/documents/{document_id}/move")
        async def move_indexing_status(
            document_id: UUID, request: Request, body: dict = Body(...)
        ):
            account = await document_caller(request)
            row = self._intake.rows.get(document_id)
            if row is None or row[0] != account.id:
                from usecase.document.errors import DocumentNotFound

                raise DocumentNotFound()
            document = row[1]
            try:
                updated = document.transition(body["status"])
            except InvalidStatusTransition:
                return JSONResponse(
                    status_code=409,
                    content={
                        "code": "invalid_status_transition",
                        "message": "Status transition is not allowed",
                    },
                )
            await self._intake.save(updated)
            from adapters.http.documents import _json

            return _json(updated)

        @app.post("/acceptance/documents/{document_id}/stale-save")
        async def stale_save_from_load(
            document_id: UUID, request: Request, body: dict = Body(...)
        ):
            account = await document_caller(request)
            row = self._intake.rows.get(document_id)
            if row is None or row[0] != account.id:
                from usecase.document.errors import DocumentNotFound

                raise DocumentNotFound()
            base = self.probe.held_load(str(document_id), int(body["load"]))
            toward = body["status"]
            if toward == "ready":
                updated = base.ready(1, 2)
            elif toward == "failed":
                updated = base.failed("forced")
            else:
                updated = base.transition(toward)
            await self._intake.save(updated)
            from adapters.http.documents import _json

            return _json(updated)

        self._server = uvicorn.Server(
            uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)
        )
        self._thread = threading.Thread(target=self._server.run, daemon=True)

    async def _index_loop(self, ctx: AppContext) -> None:
        while not self._server.should_exit:
            if self.probe.indexing_released():
                await ctx.index_documents.index_waiting()
            await asyncio.sleep(0.05)

    def start(self) -> None:
        self.logs.attach()
        self._thread.start()
        self._wait_until_ready(time.monotonic() + 10)

    def _wait_until_ready(self, deadline: float) -> None:
        ready = False
        while time.monotonic() < deadline and not ready:
            ready = self._health_ok()
        if not ready:
            raise RuntimeError("acceptance backend did not become ready")

    def _health_ok(self) -> bool:
        try:
            response = httpx.get(self.base_url + "/health", timeout=0.5)
        except httpx.HTTPError:
            time.sleep(0.05)
            return False
        return response.status_code == 200

    def stop(self) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=5)
        self.logs.detach()

    def _run_on_loop(self, coro):
        if self._loop is None:
            raise RuntimeError("acceptance server loop is not ready")
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout=60)

    def _run_second_indexing_sync(self, document_id: str) -> None:
        self._run_on_loop(self._second_indexing_run(document_id))

    def _run_dual_claim_race_sync(self) -> None:
        self._run_on_loop(self._dual_claim_race())

    async def _dual_claim_race(self) -> None:
        if self._ctx is None:
            raise RuntimeError("acceptance context is not ready")
        await asyncio.gather(
            self._ctx.index_documents.index_waiting(),
            self._ctx.index_documents.index_waiting(),
        )

    async def _second_indexing_run(self, document_id: str) -> None:
        if self._ctx is None:
            raise RuntimeError("acceptance context is not ready")
        uid = UUID(document_id)
        intake = self._ctx.index_documents.intake
        row = intake.rows.get(uid)
        if row is None:
            raise KeyError(document_id)
        content = intake.bodies.get(uid) or b""
        await self._ctx.index_documents._index(row[1], content)
