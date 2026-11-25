from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from adapters.document_status.notifying_intake import NotifyingDocumentIntake
from adapters.http.document_status_hub import DocumentStatusHub
from adapters.memory.account_store import MemoryAccountStore
from adapters.memory.chat_store import MemoryChatStore
from adapters.memory.material_search import MemoryMaterialSearch
from adapters.memory.presentation_store import MemoryPresentationStore
from adapters.memory.quiz_store import MemoryQuizStore
from adapters.memory.quiz_tutor import ScriptedQuizTutor
from adapters.search.unready_material_search import UnreadyMaterialSearch
from adapters.tutor.refusing_tutor import RefusingTutor
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
from usecase.tests.fake.presentation.fake_ocr import FakeOcr
from domain.account.identity import ProviderIdentity
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

    async def fetch_identity(self, code: str) -> ProviderIdentity:
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
    quiz_tutor: ScriptedQuizTutor
    quizzes: MemoryQuizStore
    chats: MemoryChatStore
    presentations: MemoryPresentationStore
    pieces: MemoryPieceIndex
    ocr: FakeOcr
    virus: FakeVirusCheck


def build(state_ttl: int = 600, handoff_ttl: int = 120, quiz_tutor=None) -> Bundle:
    store = MemoryAccountStore()
    clock = Clock()
    provider = ScriptedProvider()
    rates = MemoryUploadRateLimit(clock)
    tokens = JwtTokens("a" * 32, "b" * 32, timedelta(minutes=60), timedelta(days=30))
    sign_in = SignIn(
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
    chats = MemoryChatStore()
    search = MemoryMaterialSearch()
    quizzes = MemoryQuizStore()
    presentations = MemoryPresentationStore()
    ocr = FakeOcr()
    quiz_tutor = quiz_tutor or ScriptedQuizTutor()
    context = AppContext(
        RuntimeConfig(timedelta(seconds=state_ttl), ("http://localhost:5173",)),
        sign_in,
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
        ListChats(chats),
        GetChat(chats, pieces, UnreadyMaterialSearch()),
        SendMessage(chats, UnreadyMaterialSearch(), RefusingTutor()),
        **wire_quizzes(intake, search, quiz_tutor, quizzes, clock),
        **wire_presentations(intake, pieces, presentations, ocr, virus, clock),
    )
    client = TestClient(create_app(context), raise_server_exceptions=False)
    return Bundle(
        client, store, clock, provider, rates, intake, search, quiz_tutor, quizzes, chats, presentations, pieces, ocr, virus
    )


def allow(bundle: Bundle, code: str, subject: str, email: str, name: str) -> None:
    bundle.provider.by_code[code] = ProviderIdentity(subject, email, name)


def query(url: str) -> dict:
    return parse_qs(urlparse(url).query)


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def handoff(bundle: Bundle, code: str, subject: str, email: str, name: str) -> str:
    allow(bundle, code, subject, email, name)
    started = bundle.client.get("/api/v1/auth/oauth/yandex/start", follow_redirects=False)
    state = query(started.headers["location"])["state"][0]
    back = bundle.client.get(
        "/api/v1/auth/oauth/yandex/callback",
        params={"code": code, "state": state},
        follow_redirects=False,
    )
    return query(back.headers["location"])["code"][0]


def sign_in(bundle: Bundle, code="ada", subject="ya-ada", email="ada@yandex.ru", name="Ада"):
    issued = handoff(bundle, code, subject, email, name)
    return bundle.client.post("/api/v1/auth/oauth/exchange", json={"code": issued})


def auth_profile(bundle: Bundle, token: str):
    return bundle.client.get("/api/v1/user/profile", headers=bearer(token))
