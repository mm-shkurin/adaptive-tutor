import os
from datetime import timedelta

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from adapters.cache.redis_oauth import RedisOAuthStore
from adapters.cache.redis_revocations import RedisRevocations
from adapters.cache.redis_upload_rate import RedisUploadRateLimit
from adapters.document_status.notifying_intake import NotifyingDocumentIntake
from adapters.embeddings.http_embeddings import HttpEmbeddings
from adapters.filestore.file_store import PostgresFileStore
from adapters.http.document_status_hub import DocumentStatusHub
from adapters.oauth.fake import FakeOAuthProvider
from adapters.oauth.yandex import YandexOAuthProvider
from adapters.pdfreader.pdf_reader import PyPdfReader
from adapters.persistence.account_store import PostgresAccountStore
from adapters.pieceindex.piece_index import PostgresPieceIndex
from adapters.search.http_qdrant import HttpQdrant
from adapters.search.qdrant_pieces import QdrantPieces
from adapters.storage.chat_store import PostgresChatStore
from adapters.storage.document_intake import PostgresDocumentIntake
from adapters.storage.presentation_store import PostgresPresentationStore
from adapters.storage.quiz_store import PostgresQuizStore
from adapters.tutor.http_quiz import HttpQuiz
from adapters.tutor.http_tutor import HttpTutor
from adapters.tokens.jwt_tokens import JwtTokens
from adapters.virus.clamav import ClamavVirusCheck
from application.context import AppContext, RuntimeConfig
from application.presentation_wiring import wire_presentations
from application.quiz_wiring import wire_quizzes
from application.settings import Settings
from usecase.account.profile import ProfileService
from usecase.account.session import SessionService
from usecase.account.sign_in import SignIn
from usecase.chat.create_chat import CreateChat
from usecase.chat.get_chat import GetChat
from usecase.chat.list_chats import ListChats
from usecase.chat.open_chat import OpenChat
from usecase.chat.send_message import SendMessage
from usecase.document.index_documents import IndexDocuments
from usecase.document.list_documents import ListDocuments
from usecase.document.read_document import ReadDocument
from usecase.document.submit_document import SubmitDocument
from usecase.quiz.wipe import QuizWipe


def production_context(settings: Settings) -> AppContext:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    accounts = PostgresAccountStore(sessions)
    redis = Redis.from_url(settings.redis_url)
    tokens = JwtTokens(
        settings.jwt_access_secret,
        settings.jwt_refresh_secret,
        settings.access_ttl,
        settings.refresh_ttl,
    )
    provider = _provider(settings)
    hub = DocumentStatusHub()
    intake = NotifyingDocumentIntake(PostgresDocumentIntake(sessions), hub)
    files = PostgresFileStore(sessions)
    pieces = PostgresPieceIndex(sessions)
    reader = PyPdfReader()
    clock = _WallClock()
    chats = PostgresChatStore(sessions)
    quizzes = PostgresQuizStore(sessions)
    presentations = PostgresPresentationStore(sessions)
    vectors = QdrantPieces(
        HttpEmbeddings(settings.free_llm_api_url, settings.free_llm_api_key),
        HttpQdrant(settings.qdrant_url, settings.qdrant_api_key),
        pieces,
    )
    return AppContext(
        config=RuntimeConfig(settings.state_ttl, settings.cors_origins),
        sign_in=SignIn(
            provider,
            RedisOAuthStore(redis),
            accounts,
            tokens,
            clock,
            settings.state_ttl,
            settings.handoff_ttl,
            settings.frontend_callback_url,
        ),
        session=SessionService(accounts, tokens, RedisRevocations(redis)),
        profile=ProfileService(accounts, settings.public_base_url, (QuizWipe(quizzes),)),
        accounts=accounts,
        submit_document=SubmitDocument(
            intake,
            RedisUploadRateLimit(redis, clock),
            ClamavVirusCheck(settings.clamav_host, settings.clamav_port),
        ),
        read_document=ReadDocument(intake),
        list_documents=ListDocuments(intake),
        index_documents=IndexDocuments(intake, files, reader, pieces, vectors=vectors),
        status_hub=hub,
        create_chat=(create := CreateChat(intake, chats, clock)),
        open_chat=OpenChat(create, chats),
        list_chats=ListChats(chats),
        get_chat=GetChat(chats, pieces, vectors),
        send_message=SendMessage(
            chats,
            vectors,
            HttpTutor(
                settings.free_llm_chat_url,
                settings.free_llm_api_key,
                timeout=float(os.environ.get("CHAT_LATENCY_SECONDS", "5")),
            ),
            clock,
            latency=timedelta(seconds=int(os.environ.get("CHAT_LATENCY_SECONDS", "5"))),
        ),
        **wire_quizzes(
            intake,
            vectors,
            HttpQuiz(
                settings.free_llm_chat_url,
                settings.free_llm_api_key,
                timeout=float(os.environ.get("CHAT_LATENCY_SECONDS", "5")),
            ),
            quizzes,
            clock,
        ),
        **wire_presentations(
            intake,
            pieces,
            presentations,
            _noop_ocr(),
            ClamavVirusCheck(settings.clamav_host, settings.clamav_port),
            clock,
        ),
    )


def _provider(settings: Settings):
    if settings.oauth_provider == "fake":
        return FakeOAuthProvider(settings.yandex_redirect_uri)
    return YandexOAuthProvider(
        settings.yandex_client_id,
        settings.yandex_client_secret,
        settings.yandex_redirect_uri,
        settings.yandex_authorize_url,
        settings.yandex_token_url,
        settings.yandex_info_url,
    )


class _WallClock:
    def now(self):
        from datetime import datetime, timezone

        return datetime.now(timezone.utc)


def _noop_ocr():
    from usecase.tests.fake.presentation.fake_ocr import FakeOcr

    return FakeOcr()