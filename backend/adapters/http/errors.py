from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from domain.account.name import NameNotAllowed
from domain.account.photo import PhotoNotAllowed, PhotoTooLarge
from domain.chat.chat import (
    ChoiceRequired,
    ChoiceUnknown,
    DocumentNotReady,
    NotAskable,
    TellUnavailable,
)
from domain.chat.learning import EmptyQuestion, ModeNotListed, ModelNotListed
from domain.quiz.errors import DocumentNotReady as QuizDocumentNotReady
from domain.quiz.errors import EmptyRetrieval, EmptyTopic, GenerationFailed, InvalidChoice
from domain.quiz.errors import InvalidIdempotencyKey, InvalidQuestionCount, NoOpenAttempt, Unanswered
from usecase.account.errors import StoreUnavailable as AccountStoreUnavailable
from usecase.account.errors import Unauthorized
from usecase.chat.errors import ChatNotFound
from usecase.chat.errors import NoReadyDocument
from usecase.chat.errors import StoreUnavailable as ChatStoreUnavailable
from usecase.document.errors import DocumentNotFound, InvalidDocument, RateLimited, RateUnavailable
from domain.presentation.errors import (
    EmptyAdd,
    FileTooLarge,
    InvalidImage,
    InvalidSlideOrder,
    NoSlides,
    PdfNotReady,
    PdfPageMissing,
    SlideLimit,
    TextOnDraftBytes,
    TitleTooLong,
    TooManySlides,
    UnknownSlide,
)
from usecase.presentation.errors import PresentationNotFound
from usecase.presentation.errors import StoreUnavailable as PresentationStoreUnavailable
from usecase.presentation.get_progress import ProgressNotFound
from usecase.quiz.errors import QuizNotFound
from usecase.quiz.errors import StoreUnavailable as QuizStoreUnavailable
from usecase.document.errors import StoreUnavailable as DocumentStoreUnavailable

_UNAUTHORIZED = {"code": "unauthorized", "message": "Credentials are not valid"}
_INVALID = {"code": "invalid_request", "message": "The request is not valid"}
_NAME = {"code": "invalid_name", "message": "Name is not allowed"}
_PHOTO = {"code": "invalid_photo", "message": "Photo is not allowed"}
_LARGE = {"code": "photo_too_large", "message": "Photo is too large"}
_STORE = {"code": "unavailable", "message": "The account store is unreachable"}
_FINISHED = {"code": "unavailable", "message": "The request could not be finished"}
_DOCUMENT_MISSING = {"code": "document_not_found", "message": "Document was not found"}
_CHAT_MISSING = {"code": "chat_not_found", "message": "Chat was not found"}
_NOT_READY = {"code": "document_not_ready", "message": "Document is not ready"}
_NO_READY = {"code": "no_ready_document", "message": "No ready document"}
_CHAT_STORE = {"code": "unavailable", "message": "Chat store is unavailable"}
_EMPTY = {"code": "empty_message", "message": "Message is empty"}
_MODEL = {"code": "invalid_model", "message": "Model is not allowed"}
_MODE = {"code": "invalid_mode", "message": "Mode is not allowed"}
_NOT_ASKABLE = {"code": "not_askable", "message": "Material cannot be asked yet"}
_TELL = {"code": "tell_unavailable", "message": "Nothing is withheld"}
_CHOICE_REQUIRED = {"code": "choice_required", "message": "Choice is required"}
_CHOICE_UNKNOWN = {"code": "choice_unknown", "message": "Choice is not on the question"}
_QUIZ_MISSING = {"code": "quiz_not_found", "message": "Quiz was not found"}
_EMPTY_TOPIC = {"code": "empty_topic", "message": "Topic is empty"}
_BAD_COUNT = {"code": "invalid_question_count", "message": "Question count is not allowed"}
_EMPTY_RETRIEVAL = {"code": "empty_retrieval", "message": "Nothing was found for the topic"}
_GENERATION = {"code": "generation_failed", "message": "Quiz could not be assembled"}
_QUIZ_CHOICE = {"code": "invalid_choice", "message": "Choice is not on the question"}
_QUIZ_KEY = {"code": "invalid_idempotency_key", "message": "Idempotency key is not allowed"}
_NO_ATTEMPT = {"code": "no_open_attempt", "message": "No open attempt"}
_UNANSWERED = {"code": "unanswered", "message": "The question is not answered"}
_QUIZ_STORE = {"code": "unavailable", "message": "Quiz store is unavailable"}
_PRESENTATION_MISSING = {"code": "presentation_not_found", "message": "Presentation was not found"}
_PROGRESS_MISSING = {"code": "progress_not_found", "message": "Progress was not found"}
_NO_SLIDES = {"code": "no_slides", "message": "Presentation has no slides"}
_TOO_MANY = {"code": "too_many_slides", "message": "More than 40 slides"}
_TOO_LARGE = {"code": "file_too_large", "message": "File is too large"}
_VIRUS = {"code": "virus_detected", "message": "Virus detected"}
_BAD_IMAGE = {"code": "invalid_image", "message": "Image is not supported"}
_TITLE_LONG = {"code": "title_too_long", "message": "Title is too long"}
_UNKNOWN_SLIDE = {"code": "unknown_slide", "message": "Slide was not found"}
_BAD_ORDER = {"code": "invalid_slide_order", "message": "Slide order is not valid"}
_TEXT_DRAFT = {"code": "text_on_draft_bytes", "message": "Text edit waits for indexing"}
_EMPTY_ADD = {"code": "empty_add", "message": "No slide payload was sent"}
_PDF_NOT_READY = {"code": "pdf_not_ready", "message": "PDF is not ready"}
_PDF_PAGE_MISSING = {"code": "pdf_page_missing", "message": "PDF page was not found"}
_SLIDE_LIMIT = {"code": "slide_limit", "message": "More than 40 slides"}
_PRESENTATION_STORE = {"code": "unavailable", "message": "Presentation store is unavailable"}


def register_errors(app: FastAPI) -> None:
    app.add_exception_handler(Unauthorized, _status(401, _UNAUTHORIZED))
    app.add_exception_handler(DocumentNotFound, _status(404, _DOCUMENT_MISSING))
    app.add_exception_handler(ChatNotFound, _status(404, _CHAT_MISSING))
    app.add_exception_handler(DocumentNotReady, _status(400, _NOT_READY))
    app.add_exception_handler(NoReadyDocument, _status(400, _NO_READY))
    app.add_exception_handler(ChatStoreUnavailable, _status(503, _CHAT_STORE))
    app.add_exception_handler(EmptyQuestion, _status(400, _EMPTY))
    app.add_exception_handler(ModelNotListed, _status(400, _MODEL))
    app.add_exception_handler(ModeNotListed, _status(400, _MODE))
    app.add_exception_handler(NotAskable, _status(409, _NOT_ASKABLE))
    app.add_exception_handler(TellUnavailable, _status(400, _TELL))
    app.add_exception_handler(ChoiceRequired, _status(400, _CHOICE_REQUIRED))
    app.add_exception_handler(ChoiceUnknown, _status(400, _CHOICE_UNKNOWN))
    app.add_exception_handler(QuizNotFound, _status(404, _QUIZ_MISSING))
    app.add_exception_handler(QuizDocumentNotReady, _status(400, _NOT_READY))
    app.add_exception_handler(EmptyTopic, _status(400, _EMPTY_TOPIC))
    app.add_exception_handler(InvalidQuestionCount, _status(400, _BAD_COUNT))
    app.add_exception_handler(EmptyRetrieval, _status(400, _EMPTY_RETRIEVAL))
    app.add_exception_handler(GenerationFailed, _status(400, _GENERATION))
    app.add_exception_handler(InvalidChoice, _status(400, _QUIZ_CHOICE))
    app.add_exception_handler(InvalidIdempotencyKey, _status(400, _QUIZ_KEY))
    app.add_exception_handler(NoOpenAttempt, _status(400, _NO_ATTEMPT))
    app.add_exception_handler(Unanswered, _status(400, _UNANSWERED))
    app.add_exception_handler(QuizStoreUnavailable, _status(503, _QUIZ_STORE))
    app.add_exception_handler(PresentationNotFound, _status(404, _PRESENTATION_MISSING))
    app.add_exception_handler(ProgressNotFound, _status(404, _PROGRESS_MISSING))
    app.add_exception_handler(NoSlides, _status(400, _NO_SLIDES))
    app.add_exception_handler(TooManySlides, _status(400, _TOO_MANY))
    app.add_exception_handler(FileTooLarge, _status(400, _TOO_LARGE))
    app.add_exception_handler(InvalidImage, _status(400, _BAD_IMAGE))
    app.add_exception_handler(TitleTooLong, _status(400, _TITLE_LONG))
    app.add_exception_handler(UnknownSlide, _status(400, _UNKNOWN_SLIDE))
    app.add_exception_handler(InvalidSlideOrder, _status(400, _BAD_ORDER))
    app.add_exception_handler(TextOnDraftBytes, _status(400, _TEXT_DRAFT))
    app.add_exception_handler(EmptyAdd, _status(400, _EMPTY_ADD))
    app.add_exception_handler(PdfNotReady, _status(400, _PDF_NOT_READY))
    app.add_exception_handler(PdfPageMissing, _status(400, _PDF_PAGE_MISSING))
    app.add_exception_handler(SlideLimit, _status(400, _SLIDE_LIMIT))
    app.add_exception_handler(PresentationStoreUnavailable, _status(503, _PRESENTATION_STORE))
    app.add_exception_handler(InvalidDocument, _invalid_document)
    app.add_exception_handler(RateLimited, _rate_refusal)
    app.add_exception_handler(RateUnavailable, _rate_refusal)
    app.add_exception_handler(NameNotAllowed, _status(422, _NAME))
    app.add_exception_handler(PhotoNotAllowed, _status(422, _PHOTO))
    app.add_exception_handler(PhotoTooLarge, _status(413, _LARGE))
    app.add_exception_handler(AccountStoreUnavailable, _status(503, _STORE))
    app.add_exception_handler(DocumentStoreUnavailable, _status(503, _STORE))
    app.add_exception_handler(RequestValidationError, _status(422, _INVALID))
    app.add_exception_handler(Exception, _status(500, _FINISHED))


def _status(status: int, body: dict):
    async def handler(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content=body)

    return handler


async def _invalid_document(_request: Request, exc: InvalidDocument) -> JSONResponse:
    return JSONResponse(status_code=400, content={"code": exc.code, "message": exc.message})


async def _rate_refusal(_request: Request, exc: RateLimited | RateUnavailable) -> JSONResponse:
    return JSONResponse(status_code=429, content={"code": exc.code, "message": exc.message})
