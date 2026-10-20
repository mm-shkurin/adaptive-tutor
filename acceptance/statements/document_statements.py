import time
from pathlib import Path

from clients.application.document_client import DocumentClient
from clients.application.http_result import HttpResult
from clients.application.index_probe import IndexProbe
from clients.application.session_client import ScriptedProvider, SessionClient

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
LECTURE_NAME = "lecture.pdf"
NEIGHBOUR_NAME = "neighbour.pdf"
PAGE_COUNT = 1
PIECE_COUNT = 2
NEIGHBOUR_PIECE_COUNT = 1
FIVE_HUNDRED = (FIXTURES / "five_hundred.txt").read_text(encoding="utf-8")
JOINED = (FIXTURES / "joined.txt").read_text(encoding="utf-8")
EXTRACTED = (FIXTURES / "extracted.txt").read_text(encoding="utf-8")
NEIGHBOUR_TEXT = (FIXTURES / "neighbour.txt").read_text(encoding="utf-8")


class DocumentStatements:
    def __init__(self, base_url: str, provider: ScriptedProvider, probe: IndexProbe):
        self.sessions = SessionClient(base_url, provider)
        self.documents = DocumentClient(base_url)
        self.probe = probe
        self.lecture = (FIXTURES / "lecture.pdf").read_bytes()
        self.neighbour_pdf = (FIXTURES / "neighbour.pdf").read_bytes()
        self.opened = None
        self.token = ""
        self.neighbour_opened = None
        self.neighbour_token = ""
        self.neighbour_submitted = None
        self.neighbour_id = ""
        self.neighbour_ready = None
        self.upload = None
        self.read_back = None
        self.listed = None
        self.ready = None

    def given_a_signed_in_person(self) -> None:
        self.opened = self.sessions.open_account("ada@example.test", "Ada")

    def then_the_person_is_signed_in(self) -> None:
        self.token = self._signed_in(self.opened)

    def given_a_neighbour_account(self) -> None:
        self.neighbour_opened = self.sessions.open_account("boris@example.test", "Boris")

    def then_the_neighbour_is_signed_in(self) -> None:
        self.neighbour_token = self._signed_in(self.neighbour_opened)

    def when_the_neighbour_submits_a_pdf(self) -> None:
        self.neighbour_submitted = self.documents.submit_pdf(
            self.neighbour_token, NEIGHBOUR_NAME, self.neighbour_pdf
        )

    def then_the_neighbour_upload_is_waiting(self) -> None:
        submitted = self.neighbour_submitted
        assert submitted.status_code == 201
        document_id = submitted.body["id"]
        assert submitted.body == self._neighbour_waiting(document_id)
        self.neighbour_id = document_id

    def when_the_neighbour_document_becomes_ready(self) -> None:
        self.neighbour_ready = self._until_ready(self.neighbour_token, self.neighbour_id)

    def then_the_neighbour_document_is_ready(self) -> None:
        assert self.neighbour_ready.status_code == 200
        assert self.neighbour_ready.body == self._neighbour_ready(self.neighbour_id)

    def then_the_neighbour_text_is_indexed(self) -> None:
        assert self.probe.pieces_for(self.neighbour_id) == (NEIGHBOUR_TEXT,)

    def when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table(self) -> None:
        self.upload = self.documents.submit_pdf(self.token, LECTURE_NAME, self.lecture)

    def then_the_upload_is_answered_before_indexing_finishes(self) -> None:
        assert self.upload.status_code == 201
        assert self.upload.body == self._waiting(self.upload.body["id"])

    def when_the_person_reads_the_upload(self) -> None:
        self.read_back = self.documents.read(self.token, self.upload.body["id"])

    def when_the_person_lists_documents(self) -> None:
        self.listed = self.documents.list_documents(self.token)

    def then_the_next_read_shows_waiting_not_a_stale_copy(self) -> None:
        uploaded = self.upload.body
        assert self.read_back.status_code == 200
        assert self.read_back.body == uploaded
        assert self.listed.status_code == 200
        assert self.listed.body == {"documents": [uploaded], "has_next": False}

    def when_the_document_finishes_indexing(self) -> None:
        self.ready = self._until_ready(self.token, self.upload.body["id"])

    def then_the_document_becomes_ready_with_its_facts(self) -> None:
        assert self.upload.status_code == 201
        assert self.ready.status_code == 200
        assert self.ready.body == self._ready(self.upload.body["id"])

    def then_the_persons_search_finds_the_text_and_the_table(self) -> None:
        self._assert_lecture_pieces()

    def then_the_extracted_text_matches_the_pdf(self) -> None:
        assert self.probe.extracted_text(self.upload.body["id"]) == EXTRACTED

    def then_the_neighbours_text_is_absent(self) -> None:
        person_text = self.probe.extracted_text(self.upload.body["id"])
        assert person_text == EXTRACTED
        assert self.probe.pieces_for(self.neighbour_id) == (NEIGHBOUR_TEXT,)

    def then_a_piece_of_500_tokens_is_kept(self) -> None:
        self._assert_lecture_pieces()

    def then_a_shorter_piece_is_joined_onward(self) -> None:
        self._assert_lecture_pieces()

    def then_the_original_file_is_gone(self) -> None:
        assert self.probe.file_for(self.upload.body["id"]) is None

    def then_the_neighbours_file_is_still_there(self) -> None:
        assert self.probe.file_for(self.neighbour_id) == self.neighbour_pdf

    def close(self) -> None:
        self.sessions.close()
        self.documents.close()

    def _assert_lecture_pieces(self) -> None:
        assert self.probe.pieces_for(self.upload.body["id"]) == (FIVE_HUNDRED, JOINED)

    def _signed_in(self, opened: HttpResult) -> str:
        assert opened.status_code == 200
        assert opened.body["token_type"] == "bearer"
        assert opened.body["access_token"] is not None
        assert opened.body["refresh_token"] is not None
        return opened.body["access_token"]

    def _waiting(self, document_id: str) -> dict:
        return self._document(document_id, LECTURE_NAME, len(self.lecture), None, None, "waiting")

    def _neighbour_waiting(self, document_id: str) -> dict:
        return self._document(document_id, NEIGHBOUR_NAME, len(self.neighbour_pdf), None, None, "waiting")

    def _ready(self, document_id: str) -> dict:
        return self._document(document_id, LECTURE_NAME, len(self.lecture), PAGE_COUNT, PIECE_COUNT, "ready")

    def _neighbour_ready(self, document_id: str) -> dict:
        return self._document(
            document_id, NEIGHBOUR_NAME, len(self.neighbour_pdf), PAGE_COUNT, NEIGHBOUR_PIECE_COUNT, "ready"
        )

    def _document(self, document_id: str, name: str, size_bytes: int, page_count, piece_count, status: str) -> dict:
        return {
            "id": document_id,
            "name": name,
            "size_bytes": size_bytes,
            "page_count": page_count,
            "piece_count": piece_count,
            "status": status,
            "error": None,
        }

    def _until_ready(self, token: str, document_id: str):
        deadline = time.monotonic() + 30
        seen = None
        while time.monotonic() < deadline:
            seen = self.documents.read(token, document_id)
            if seen.status_code == 200 and seen.body["status"] in {"ready", "failed"}:
                break
            time.sleep(0.05)
        return seen
