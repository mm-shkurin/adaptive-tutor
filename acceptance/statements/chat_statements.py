from pathlib import Path

from clients.application.chat_client import ChatClient
from clients.application.document_client import DocumentClient
from clients.application.http_result import HttpResult
from clients.application.session_client import ScriptedProvider, SessionClient

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
OLDER_PDF = "older.pdf"
NEWER_PDF = "newer.pdf"


class ChatStatements:
    def __init__(self, base_url: str, provider: ScriptedProvider, clock):
        self.sessions = SessionClient(base_url, provider)
        self.documents = DocumentClient(base_url)
        self.chats = ChatClient(base_url)
        self.clock = clock
        self.lecture = (FIXTURES / "lecture.pdf").read_bytes()
        self.token = ""
        self.older_id = ""
        self.newer_id = ""
        self.created: HttpResult | None = None
        self.listed: HttpResult | None = None

    def given_a_signed_in_person(self) -> None:
        opened = self.sessions.open_account("ada@example.test", "Ada")
        assert opened.status_code == 200
        assert opened.body is not None
        self.token = opened.body["access_token"]

    def given_a_selected_ready_pdf_that_is_older_than_another(self) -> None:
        self.older_id = self._ready_pdf(OLDER_PDF)
        self.clock.advance(60)
        self.newer_id = self._ready_pdf(NEWER_PDF)

    def when_the_person_starts_a_chat_on_the_selected_pdf(self) -> None:
        self.created = self.chats.create(self.token, self.older_id)

    def then_the_chat_is_bound_to_the_selected_pdf(self) -> None:
        created = self._created()
        assert created.status_code == 201
        assert created.body is not None
        assert created.body["document_id"] == self.older_id
        assert created.body["document_name"] == OLDER_PDF
        assert created.body["document_id"] != self.newer_id

    def then_the_thread_is_empty(self) -> None:
        created = self._created()
        assert created.body is not None
        assert created.body["lines"] == []

    def then_the_list_row_shows_that_pdfs_name_and_no_preview(self) -> None:
        created = self._created()
        assert created.body is not None
        self.listed = self.chats.list(self.token)
        assert self.listed.status_code == 200
        assert self.listed.body == {
            "chats": [
                {
                    "id": created.body["id"],
                    "document_id": self.older_id,
                    "document_name": OLDER_PDF,
                    "preview": None,
                }
            ]
        }

    def close(self) -> None:
        self.sessions.close()
        self.documents.close()
        self.chats.close()

    def _ready_pdf(self, name: str) -> str:
        uploaded = self.documents.submit_pdf(self.token, name, self.lecture)
        assert uploaded.status_code == 201
        assert uploaded.body is not None
        document_id = uploaded.body["id"]
        indexing = self.documents.move_indexing_status(self.token, document_id, "indexing")
        assert indexing.status_code == 200
        ready = self.documents.move_indexing_status(self.token, document_id, "ready")
        assert ready.status_code == 200
        assert ready.body is not None
        assert ready.body["status"] == "ready"
        assert ready.body["name"] == name
        return document_id

    def _created(self) -> HttpResult:
        assert self.created is not None
        return self.created
