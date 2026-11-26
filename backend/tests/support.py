from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from adapters.document_status.notifying_intake import NotifyingDocumentIntake
from adapters.http.document_status_hub import DocumentStatusHub
from adapters.memory.account_store import MemoryAccountStore
from adapters.memory.chat_store import MemoryChatStore
from adapters.memory.material_search import MemoryMaterialSearch
from adapters.memory.presentation_store import MemoryPresentationStore
from adapters.memory.quiz_store import MemoryQuizStore
from adapters.memory.quiz_tutor import ScriptedQuizTutor
from adapters.memory.scripted_tutor import ScriptedTutor
from adapters.search.memory_piece_vectors import MemoryPieceVectors
from adapters.search.prefer_seeded_search import PreferSeededSearch
from adapters.memory.document_intake import MemoryDocumentIntake
from adapters.memory.file_store import MemoryFileStore
from adapters.memory.oauth_store import MemoryOAuthStore
from adapters.memory.piece_index import MemoryPieceIndex
from adapters.memory.revocations import MemoryRevocations
from adapters.memory.upload_rate_limit import MemoryUploadRateLimit
from adapters.pdfreader.pdf_reader import PyPdfReader
from adapters.tokens.jwt_tokens import JwtTokens
from application.context import AppContext, RuntimeConfig
from application.main import create_app
from application.presentation_wiring import wire_presentations
from application.quiz_wiring import wire_quizzes
from usecase.tests.fake.presentation.fake_formula_assist import FakeFormulaAssist
from usecase.tests.fake.presentation.fake_ocr import FakeOcr
from usecase.tests.fake.presentation.fake_office_parser import FakeOfficeParser
from usecase.account.profile import ProfileService
from usecase.account.session import SessionService
from usecase.account.sign_in import SignIn
from usecase.chat.create_chat import CreateChat
from usecase.chat.get_chat import GetChat
from usecase.chat.list_chats import ListChats
from usecase.chat.open_chat import OpenChat
from usecase.chat.send_message import SendMessage
from usecase.quiz.wipe import QuizWipe
from usecase.document.index_documents import IndexDocuments
from usecase.document.list_documents import ListDocuments
from usecase.document.read_document import ReadDocument
from usecase.document.submit_document import SubmitDocument
from usecase.tests.fake.document.fake_virus_check import FakeVirusCheck
from tests.support_auth import allow, auth_profile, bearer, handoff, query, sign_in

WHEN = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)
CREATED = "2024-05-06T07:08:09Z"
JPEG = b"\xff\xd8\xff" + b"\x00" * 16
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
WEBP = b"RIFF" + (24).to_bytes(4, "little") + b"WEBP" + b"\x00" * 12
GIF = b"GIF89a" + b"\x00" * 16


class Clock:
    def __init__(self):
        self.moment = WHEN

    def now(self):
        return self.moment

    def advance(self, seconds: int) -> None:
        self.moment += timedelta(seconds=seconds)


class ScriptedProvider:
    name = "yandex"

    def __init__(self):
        self.by_code = {}
        self.calls = 0

    def authorization_url(self, state: str) -> str:
        return f"https://oauth.yandex.ru/authorize?state={state}"

    async def fetch_identity(self, code: str):
        self.calls += 1
        outcome = self.by_code[code]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@dataclass
class Bundle:
    client: TestClient
    store: MemoryAccountStore
    clock: Clock
    provider: ScriptedProvider
    rates: MemoryUploadRateLimit
    intake: NotifyingDocumentIntake
    search: MemoryMaterialSearch
    tutor: ScriptedTutor
    quiz_tutor: ScriptedQuizTutor
    quizzes: MemoryQuizStore
    chats: MemoryChatStore
    presentations: MemoryPresentationStore
    pieces: MemoryPieceIndex
    ocr: FakeOcr
    formulas: FakeFormulaAssist
    office: FakeOfficeParser
    virus: FakeVirusCheck


def build(state_ttl: int = 600, handoff_ttl: int = 120, quiz_tutor=None) -> Bundle:
    store = MemoryAccountStore()
    clock = Clock()
    provider = ScriptedProvider()
    rates = MemoryUploadRateLimit(clock)
    tokens = JwtTokens("a" * 32, "b" * 32, timedelta(minutes=60), timedelta(days=30))
    sign_in_uc = SignIn(
        provider,
        MemoryOAuthStore(),
        store,
        tokens,
        clock,
        timedelta(seconds=state_ttl),
        timedelta(seconds=handoff_ttl),
        "http://localhost:5173/auth/callback",
    )
    bodies = {}
    hub = DocumentStatusHub()
    intake = NotifyingDocumentIntake(MemoryDocumentIntake(bodies), hub)
    files = MemoryFileStore(bodies)
    pieces = MemoryPieceIndex()
    virus = FakeVirusCheck()
    reader = PyPdfReader()
    chats = MemoryChatStore(clock)
    quizzes = MemoryQuizStore(clock)
    presentations = MemoryPresentationStore()
    ocr = FakeOcr()
    formulas = FakeFormulaAssist()
    office = FakeOfficeParser()
    quiz_tutor = quiz_tutor or ScriptedQuizTutor()
    tutor = ScriptedTutor()
    vectors = MemoryPieceVectors(pieces)
    search = PreferSeededSearch(MemoryMaterialSearch(), vectors, clock)
    context = AppContext(
        RuntimeConfig(timedelta(seconds=state_ttl), ("http://localhost:5173",)),
        sign_in_uc,
        SessionService(store, tokens, MemoryRevocations()),
        ProfileService(store, "http://testserver", (QuizWipe(quizzes),)),
        store,
        SubmitDocument(intake, rates, virus),
        ReadDocument(intake),
        ListDocuments(intake),
        IndexDocuments(intake, files, reader, pieces),
        hub,
        (create := CreateChat(intake, chats, clock)),
        OpenChat(create, chats),
        ListChats(chats, intake),
        GetChat(chats, pieces, vectors, intake),
        SendMessage(chats, search, tutor, clock),
        **wire_quizzes(intake, search, quiz_tutor, quizzes, clock),
        **wire_presentations(
            intake, pieces, presentations, ocr, virus, clock, quizzes, chats, files, reader, office, formulas
        ),
    )
    client = TestClient(create_app(context), raise_server_exceptions=False)
    return Bundle(
        client,
        store,
        clock,
        provider,
        rates,
        intake,
        search,
        tutor,
        quiz_tutor,
        quizzes,
        chats,
        presentations,
        pieces,
        ocr,
        formulas,
        office,
        virus,
    )


__all__ = [
    "Bundle",
    "CREATED",
    "Clock",
    "GIF",
    "JPEG",
    "PNG",
    "ScriptedProvider",
    "WEBP",
    "WHEN",
    "allow",
    "auth_profile",
    "bearer",
    "build",
    "handoff",
    "query",
    "sign_in",
]
