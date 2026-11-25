import asyncio
import os
from dataclasses import dataclass
from datetime import timedelta

from adapters.http.document_status_hub import DocumentStatusHub
from application.settings import load_settings
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
from usecase.quiz.create_quiz import CreateQuiz
from usecase.quiz.play import AdvanceQuiz, AnswerQuiz, RetryQuiz
from usecase.quiz.read import GetQuiz, ListQuizzes


@dataclass
class RuntimeConfig:
    state_ttl: timedelta
    cors_origins: tuple[str, ...]


@dataclass
class AppContext:
    config: RuntimeConfig
    sign_in: SignIn
    session: SessionService
    profile: ProfileService
    accounts: object
    submit_document: SubmitDocument
    read_document: ReadDocument
    list_documents: ListDocuments
    index_documents: IndexDocuments
    status_hub: DocumentStatusHub
    create_chat: CreateChat
    open_chat: OpenChat
    list_chats: ListChats
    get_chat: GetChat
    send_message: SendMessage
    _indexing: asyncio.Event | None = None
    create_quiz: CreateQuiz | None = None
    list_quizzes: ListQuizzes | None = None
    get_quiz: GetQuiz | None = None
    answer_quiz: AnswerQuiz | None = None
    advance_quiz: AdvanceQuiz | None = None
    retry_quiz: RetryQuiz | None = None
    create_presentation: object | None = None
    get_presentation: object | None = None
    patch_presentation: object | None = None
    delete_presentation: object | None = None
    add_slides: object | None = None
    index_presentation: object | None = None
    get_progress: object | None = None

    def schedule_indexing(self) -> None:
        if self._indexing is None:
            return
        self._indexing.set()


def build_production_context(env=None) -> AppContext:
    from application.context_build import production_context

    settings = load_settings(os.environ if env is None else env)
    return production_context(settings)