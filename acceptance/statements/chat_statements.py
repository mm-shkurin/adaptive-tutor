import time
from pathlib import Path

from clients.application.chat_client import ChatClient
from clients.application.document_client import DocumentClient
from clients.application.http_result import HttpResult
from clients.application.session_client import ScriptedProvider, SessionClient
from statements.chat_gate_statements import ChatGateStatements
from statements.chat_security_statements import ChatSecurityStatements
from statements.empty_vector_statements import EmptyVectorStatements
from statements.failed_reply_statements import FailedReplyStatements
from statements.interleave_send_statements import InterleaveSendStatements
from statements.interleave_vector_statements import InterleaveVectorStatements
from statements.latency_statements import LatencyStatements
from statements.list_order_statements import ListOrderStatements
from statements.partial_vector_statements import PartialVectorStatements
from statements.reply_statements import LECTURE, MODEL, SCRIPT, ReplyStatements
from statements.session_store_fail_statements import SessionStoreFailStatements
from statements.switch_chat_statements import SwitchChatStatements
from statements.vector_open_statements import VectorOpenStatements
from statements.vector_reuse_statements import VectorReuseStatements

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
OLDER_PDF = "older.pdf"
NEWER_PDF = "newer.pdf"
CONTAINED = "w0001"


class ChatStatements(
    VectorOpenStatements,
    ReplyStatements,
    FailedReplyStatements,
    VectorReuseStatements,
    PartialVectorStatements,
    LatencyStatements,
    InterleaveVectorStatements,
    EmptyVectorStatements,
    SwitchChatStatements,
    ChatGateStatements,
    ChatSecurityStatements,
    ListOrderStatements,
    InterleaveSendStatements,
    SessionStoreFailStatements,
):
    def __init__(self, base_url: str, provider: ScriptedProvider, clock, probe=None, fakes=None):
        self.sessions = SessionClient(base_url, provider)
        self.documents = DocumentClient(base_url)
        self.chats = ChatClient(base_url)
        self.clock = clock
        self.probe = probe
        self.fakes = fakes
        self.lecture = (FIXTURES / "lecture.pdf").read_bytes()
        self.token = ""
        self.older_id = ""
        self.newer_id = ""
        self.created: HttpResult | None = None
        self.opened: HttpResult | None = None
        self.listed: HttpResult | None = None
        self.piece_writes_before = 0

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

    def and_a_new_pdf_that_finishes_indexing(self) -> None:
        uploaded = self.documents.submit_pdf(self.token, LECTURE, self.lecture)
        assert uploaded.status_code == 201
        assert uploaded.body is not None
        self.document_id = uploaded.body["id"]
        opened = self.sessions.open_account("neil@example.test", "Neil")
        assert opened.status_code == 200
        assert opened.body is not None
        neighbour = self.documents.submit_pdf(
            opened.body["access_token"],
            "neighbour.pdf",
            (FIXTURES / "neighbour.pdf").read_bytes(),
        )
        assert neighbour.status_code == 201
        assert neighbour.body is not None
        self.neighbour_id = neighbour.body["id"]
        self.probe.release_indexing()
        finished = self._until_terminal(self.token, self.document_id)
        neighbour_finished = self._until_terminal(opened.body["access_token"], self.neighbour_id)
        assert finished.body["status"] == "ready"
        assert neighbour_finished.body["status"] == "ready"
        assert self.probe.file_for(self.document_id) is None
        self.stored_pieces = self.probe.pieces_for(self.document_id)
        self.stored_pages = self.probe.pages_for(self.document_id)
        self.neighbour_pieces = self.probe.pieces_for(self.neighbour_id)

    def when_the_person_asks_a_question_that_the_pdf_contains(self) -> None:
        self.created = self.chats.create(self.token, self.document_id)
        assert self.created.status_code == 201
        assert self.created.body is not None
        self.chat_id = self.created.body["id"]
        scripted = self.chats.script_tutor(self.token, SCRIPT)
        assert scripted.status_code == 204
        self.sent = self.chats.send(self.token, self.chat_id, CONTAINED, MODEL, "professor", "attempt-indexed")

    def then_the_vectors_are_384_dimensional(self) -> None:
        found = self.chats.vectors(self.token, self.document_id)
        assert found.status_code == 200
        assert found.body == {
            "model": "all-MiniLM-L6-v2",
            "dimensions": [384] * len(self.stored_pieces),
            "pages": list(self.stored_pages),
            "texts": list(self.stored_pieces),
        }
        assert found.body["dimensions"]
        assert set(found.body["dimensions"]) == {384}

    def then_the_reply_uses_only_pieces_of_this_pdf(self) -> None:
        sources = self._sent().body["lines"][1]["sources"]
        texts = [source["text"] for source in sources]
        assert texts
        assert set(texts) <= set(self.stored_pieces)
        assert self.neighbour_pieces
        assert not set(texts) & set(self.neighbour_pieces)

    def then_the_page_is_the_starting_page_stored_while_the_file_was_in_hand(self) -> None:
        tutor = self._sent().body["lines"][1]
        first = tutor["sources"][0]
        stored = self.stored_pages[self.stored_pieces.index(first["text"])]
        assert self.probe.file_for(self.document_id) is None
        assert isinstance(stored, int) and stored >= 1
        assert tutor["page"] == stored
        assert first["page"] == stored

    def close(self) -> None:
        self.sessions.close()
        self.documents.close()
        self.chats.close()

    def _ready_pdf(self, name: str, token: str | None = None) -> str:
        auth = self.token if token is None else token
        uploaded = self.documents.submit_pdf(auth, name, self.lecture)
        assert uploaded.status_code == 201
        assert uploaded.body is not None
        document_id = uploaded.body["id"]
        indexing = self.documents.move_indexing_status(auth, document_id, "indexing")
        assert indexing.status_code == 200
        ready = self.documents.move_indexing_status(auth, document_id, "ready")
        assert ready.status_code == 200
        assert ready.body is not None
        assert ready.body["status"] == "ready"
        assert ready.body["name"] == name
        return document_id

    def _until_terminal(self, token: str, document_id: str):
        deadline = time.monotonic() + 30
        seen = None
        while time.monotonic() <= deadline:
            seen = self.documents.read(token, document_id)
            if seen.status_code == 200 and seen.body is not None and seen.body["status"] in {"ready", "failed"}:
                return seen
            time.sleep(0.05)
        assert seen is not None
        return seen

    def _created(self) -> HttpResult:
        assert self.created is not None
        return self.created
