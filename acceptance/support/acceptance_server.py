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

from adapters.document_status.notifying_intake import NotifyingDocumentIntake
from adapters.http.document_status_hub import DocumentStatusHub
from adapters.memory.account_store import MemoryAccountStore
from adapters.memory.chat_store import MemoryChatStore
from support.counting_chat_store import CountingChatStore
from adapters.embeddings.http_embeddings import HttpEmbeddings
from adapters.memory.material_search import MemoryMaterialSearch
from adapters.search.http_qdrant import HttpQdrant
from adapters.search.prefer_seeded_search import PreferSeededSearch
from adapters.search.qdrant_pieces import QdrantPieces
from adapters.memory.quiz_store import MemoryQuizStore
from adapters.memory.quiz_tutor import ScriptedQuizTutor
from adapters.memory.scripted_tutor import ScriptedTutor
from adapters.memory.document_intake import MemoryDocumentIntake
from adapters.memory.file_store import MemoryFileStore
from adapters.memory.oauth_store import MemoryOAuthStore
from clients.application.probe_piece_index import ProbePieceIndex
from clients.application.probe_virus_check import ProbeVirusCheck
from adapters.memory.revocations import MemoryRevocations
from adapters.memory.upload_rate_limit import MemoryUploadRateLimit
from adapters.pdfreader.pdf_reader import PyPdfReader
from clients.application.probe_gated_pdf_reader import ProbeGatedPdfReader
from adapters.tokens.jwt_tokens import JwtTokens
from domain.document.document import InvalidStatusTransition
from application.context import AppContext, RuntimeConfig
from application.main import create_app
from adapters.memory.presentation_store import MemoryPresentationStore
from application.presentation_wiring import wire_presentations
from application.quiz_wiring import wire_quizzes
from clients.application.index_probe import IndexProbe
from clients.application.peak_chat_hold import PeakChatHold
from clients.application.session_client import ScriptedProvider
from usecase.account.profile import ProfileService
from usecase.account.session import SessionService
from usecase.account.sign_in import SignIn
from support.chat_probe import register_chat_probe
from support.vector_fakes import ExternalFakes
from usecase.chat.create_chat import CreateChat
from usecase.chat.get_chat import GetChat
from usecase.chat.list_chats import ListChats
from usecase.chat.open_chat import OpenChat
from usecase.chat.send_message import SendMessage
from usecase.quiz.wipe import QuizWipe
from clients.application.probe_index_documents import ProbeIndexDocuments
from usecase.document.list_documents import ListDocuments
from usecase.document.read_document import ReadDocument
from usecase.document.search_documents import SearchDocuments
from usecase.document.submit_document import SubmitDocument
from usecase.tests.fake.presentation.fake_formula_assist import FakeFormulaAssist
from usecase.tests.fake.presentation.fake_ocr import FakeOcr
from usecase.tests.fake.presentation.fake_office_parser import FakeOfficeParser
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
        self.peak_chat_hold = PeakChatHold()
        self.clock = _Clock()
        self.rates = MemoryUploadRateLimit(self.clock)
        self.logs = LogCapture()
        self.fakes = ExternalFakes()
        self.fakes.start()
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
        self._accounts = store
        tokens = JwtTokens(
            DISCLOSURE_KNOWN_SECRET, "b" * 32, timedelta(minutes=60), timedelta(days=30)
        )
        bodies: dict[UUID, bytes] = {}
        hub = DocumentStatusHub()
        raw_intake = MemoryDocumentIntake(bodies, self.probe, now=self.clock.now)
        intake = NotifyingDocumentIntake(raw_intake, hub)
        files = MemoryFileStore(bodies, self.probe)
        pieces = ProbePieceIndex(self.probe)
        self.probe.attach_intake(raw_intake)
        self.probe.attach_pieces(pieces)
        self._intake = intake
        self._pieces = pieces
        reader = ProbeGatedPdfReader(PyPdfReader(), self.probe)
        chats = CountingChatStore(MemoryChatStore())
        vectors = QdrantPieces(
            HttpEmbeddings(self.fakes.embeddings_url, "", timeout=0.4),
            HttpQdrant(self.fakes.qdrant_url, ""),
            pieces,
        )
        search = PreferSeededSearch(MemoryMaterialSearch(), vectors, self.clock)
        tutor = ScriptedTutor()
        self._search = search
        self._vectors = vectors
        self._tutor = tutor
        self._chats = chats
        quizzes = MemoryQuizStore()
        quiz_tutor = ScriptedQuizTutor()
        self._quizzes = quizzes
        self._quiz_tutor = quiz_tutor
        virus = ProbeVirusCheck(self.probe)
        presentations = MemoryPresentationStore()
        ocr = FakeOcr()
        formulas = FakeFormulaAssist()
        office = FakeOfficeParser()
        self._presentations = presentations
        self._ocr = ocr
        return AppContext(
            RuntimeConfig(_state_ttl(), ("http://localhost:5173",)),
            self._sign_in(store, tokens),
            SessionService(store, tokens, MemoryRevocations()),
            ProfileService(store, self.base_url, (QuizWipe(quizzes),)),
            store,
            SubmitDocument(intake, self.rates, virus),
            ReadDocument(intake),
            ListDocuments(intake),
            ProbeIndexDocuments(intake, files, reader, pieces, self.probe, self.clock, vectors),
            hub,
            (create := CreateChat(intake, chats, self.clock)),
            OpenChat(create, chats),
            ListChats(chats, intake),
            GetChat(chats, pieces, vectors, intake),
            SendMessage(chats, search, tutor, self.clock, latency=timedelta(milliseconds=50)),
            self._indexing,
            **wire_quizzes(intake, search, quiz_tutor, quizzes, self.clock),
            **wire_presentations(
                intake,
                pieces,
                presentations,
                ocr,
                virus,
                self.clock,
                quizzes,
                chats,
                files,
                reader,
                office,
                formulas,
            ),
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
        register_chat_probe(app, self._search, self._tutor, self._intake, self._vectors)
        from support.quiz_probe import register_quiz_probe

        register_quiz_probe(app, self._quiz_tutor)
        app.router.lifespan_context = lifespan
        app.state.index_probe = self.probe
        app.state.peak_chat_hold = self.peak_chat_hold
        app.state.accounts = self._accounts
        search = SearchDocuments(self._intake, self._pieces)

        from adapters.http.documents import _caller as document_caller

        @app.get("/acceptance/documents/{document_id}/searchable-pieces")
        async def searchable_pieces(document_id: UUID, request: Request):
            account = await document_caller(request)
            found = await search.pieces_for(account.id, document_id)
            return {"pieces": list(found)}

        @app.get("/acceptance/documents/{document_id}/vectors")
        async def stored_vectors(document_id: UUID, request: Request):
            account = await document_caller(request)
            row = self._intake.rows.get(document_id)
            if row is None or row[0] != account.id:
                from usecase.document.errors import DocumentNotFound

                raise DocumentNotFound()
            return self.fakes.vectors_for(str(document_id))

        @app.get("/acceptance/documents/{document_id}/vector-failure")
        async def vector_failure(document_id: UUID, request: Request):
            account = await document_caller(request)
            row = self._intake.rows.get(document_id)
            if row is None or row[0] != account.id:
                from usecase.document.errors import DocumentNotFound

                raise DocumentNotFound()
            return {"ordinal": self._vectors.failed_ordinal(document_id)}

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
        self.fakes.stop()
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
