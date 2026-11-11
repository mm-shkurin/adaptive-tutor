import json
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import jwt

from usecase.document.list_documents import PAGE_SIZE

from clients.application.document_client import DocumentClient
from clients.application.http_result import HttpResult
from clients.application.index_probe import IndexProbe
from clients.application.peak_chat_client import PEAK_CHAT_IN_FLIGHT, PeakChatClient
from clients.application.session_client import ScriptedProvider, SessionClient
from support.disclosure_constants import DISCLOSURE_KNOWN_SECRET, DISCLOSURE_PDF_PHRASE
from support.log_capture import LogCapture

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
MIN_BYTES = 1_048_576
MAX_BYTES = 52_428_800
EDGE_NAME = "edge.pdf"
DOCUMENT_NOT_FOUND = {"code": "document_not_found", "message": "Document was not found"}
REFUSALS = {
    "file_missing": ("file_missing", "File is missing"),
    "invalid_pdf": ("invalid_pdf", "File is not a PDF"),
    "empty_pdf": ("empty_pdf", "PDF has no text"),
    "file_too_small": ("file_too_small", "File is too small"),
    "file_too_large": ("file_too_large", "File is too large"),
    "encrypted_pdf": ("encrypted_pdf", "PDF is encrypted"),
    "name_missing": ("name_missing", "File name is missing"),
    "name_too_long": ("name_too_long", "File name is too long"),
    "virus_detected": ("virus_detected", "Virus detected"),
}
_VIRUS_OUTCOMES = {
    "finds a virus": "finds_virus",
    "times out": "times_out",
    "answers unreadable": "answers_unreadable",
}
SECOND_PDF_NAME = "second.pdf"
_PDF_HEAD = b"%PDF-1.4\n"
_PDF_TAIL = b"1 0 obj<<>>endobj\ntrailer<<>>\nstartxref\n0\n%%EOF"
LECTURE_NAME = "lecture.pdf"
NEIGHBOUR_NAME = "neighbour.pdf"
PAGE_COUNT = 1
PIECE_COUNT = 2
NEIGHBOUR_PIECE_COUNT = 1
FIVE_HUNDRED = (FIXTURES / "five_hundred.txt").read_text(encoding="utf-8")
JOINED = (FIXTURES / "joined.txt").read_text(encoding="utf-8")
EXTRACTED = (FIXTURES / "extracted.txt").read_text(encoding="utf-8")
NEIGHBOUR_TEXT = (FIXTURES / "neighbour.txt").read_text(encoding="utf-8")
MANY_PIECES_NAME = "many_pieces.pdf"
TABLE_NAMED = "|Topic|Mark|\n|---|---|\n|Limits|91|"
HOSTILE_MARKUP = "' OR 1=1<script>"
HOSTILE_NAME = f"report{HOSTILE_MARKUP}\nline-two.pdf"
HOSTILE_FAILURE_REASON = f"{HOSTILE_MARKUP}\n{TABLE_NAMED}"
HOSTILE_PDF_TEXT = "' OR 1=1"
UNKNOWN_STATUS = "corrupted"
LONG_PDF_NAME = "а" * 251 + ".pdf"
OVERLONG_PDF_NAME = "а" * 252 + ".pdf"
PATHOLOGICAL_NAME = "pathological.pdf"
INDEXING_LIMIT_SECONDS = 300
STANDARD_LECTURE_BYTES = 10 * 1024 * 1024
INDEXING_CEILING_SECONDS = 30
_ACCESS_SECRET = DISCLOSURE_KNOWN_SECRET
_DISCLOSURE_STACK_MARKERS = (
    "Traceback (most recent call last)",
    'File "',
)
_DISCLOSURE_PATH_MARKERS = (
    "OneDrive\\Desktop\\adaptive-tutor",
    "/adaptive-tutor/backend/",
)
_DISCLOSURE_INTERNAL_MARKERS = (
    "ProbePieceIndex",
    "ProbeVirusCheck",
    "ProbeIndexDocuments",
    "MemoryDocumentIntake",
    "StoreUnavailable",
)
HOSTILE_DOCUMENT_ID = "00000000-0000-0000-0000-000000000001"
HOSTILE_OWNER_ID = "00000000-0000-0000-0000-000000000002"
HOSTILE_PAGE_COUNT = "999"
HOSTILE_PIECE_COUNT = "888"
HOSTILE_STATUS = "ready"
HOSTILE_ERROR = "injected"
HOSTILE_SIZE_BYTES = "99999999"
HOSTILE_UPLOAD_TIME = "1970-01-01T00:00:00Z"
BATCH_RETRY_DOCUMENT_COUNT = 5
SPLIT_LETTER_PDF_NAME = ("я" * 254) + "е\u0301"
NAIVE_BROKEN_NAME = SPLIT_LETTER_PDF_NAME[:255]


class DocumentStatements:
    PEAK_CHAT_EMAIL = "peak-chat-load@example.test"
    PEAK_CHAT_NAME = "Peak Chat Load"

    def __init__(
        self,
        base_url: str,
        provider: ScriptedProvider,
        probe: IndexProbe,
        clock=None,
        rates=None,
        logs: LogCapture | None = None,
    ):
        self._base_url = base_url
        self.sessions = SessionClient(base_url, provider)
        self.documents = DocumentClient(base_url)
        self.peak_chat_client: PeakChatClient | None = None
        self.probe = probe
        self.clock = clock
        self.rates = rates
        self.logs = logs
        self.known_secret = ""
        self.pdf_phrase = ""
        self.pdf_with_phrase = b""
        self.not_pdf_with_phrase = b""
        self.disclosure_answer_text = ""
        self.lecture = (FIXTURES / "lecture.pdf").read_bytes()
        self.hostile_query_pdf = (FIXTURES / "hostile_query.pdf").read_bytes()
        self.neighbour_pdf = (FIXTURES / "neighbour.pdf").read_bytes()
        self.many_pieces = (FIXTURES / "many_pieces.pdf").read_bytes()
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
        self.first_page = None
        self.next_page = None
        self.person_upload_ids: list[str] = []
        self.pair_ids: list[str] = []
        self.first_page_order: list[str] = []
        self.second_page_order: list[str] = []
        self.ready = None
        self.failing_id = ""
        self.later_id = ""
        self.batch_document_ids: list[str] = []
        self.failing_final = None
        self.later_final = None
        self.finished = None
        self.virus_scans_before_retry = 0
        self.virus_scans_at_start = 0
        self.piece_writes_before_retry = 0
        self.pieces_before_second_index_request = 0
        self.expected_finished_status = ""
        self.edge_size = 0
        self.edge_pdf = b""
        self.canonical_submitted_name = ""
        self.stored_name = ""
        self.indexing_started_at = None
        self.short_of_five = None
        self.after_five = None
        self.searchable = None
        self.baseline_list = None
        self.baseline_connections = 0
        self.baseline_file_handles = 0
        self.baseline_temp_files = 0
        self.refusal = None
        self.neighbour_refusal = None
        self.missing_refusal = None
        self.guest_refusal = None
        self.guest_list_refusal = None
        self.guest_upload_refusal = None
        self.intake_count_before_guest = 0
        self.piece_ids_before_submit = frozenset()
        self.not_pdf = b"PLAIN" + b"x" * (MIN_BYTES - len(b"PLAIN"))
        self.under_min = _pdf_of_size(MIN_BYTES - 1)
        self.over_max = _pdf_of_size(MAX_BYTES + 1)
        self.empty_pdf = (FIXTURES / "empty_text.pdf").read_bytes()
        self.encrypted_pdf = (FIXTURES / "encrypted.pdf").read_bytes()
        self.standard_lecture = b""
        self.indexing_started_at = 0.0

    def given_a_signed_in_person(self) -> None:
        self.opened = self.sessions.open_account("ada@example.test", "Ada")

    def then_the_person_is_signed_in(self) -> None:
        self.token = self._signed_in(self.opened)

    def given_a_signed_in_person_for_peak_chat_load(self) -> None:
        self.opened = self.sessions.open_account(self.PEAK_CHAT_EMAIL, self.PEAK_CHAT_NAME)

    def given_the_peak_chat_baseline(self) -> None:
        self.peak_chat_client = PeakChatClient(self._base_url)
        self.peak_chat_client.begin_peak_load(self.token)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.peak_chat_client.peak_chat_requests_accepted() == PEAK_CHAT_IN_FLIGHT:
                break
            time.sleep(0.05)
        assert self.peak_chat_client.peak_chat_requests_accepted() == PEAK_CHAT_IN_FLIGHT

    def when_the_person_uploads_a_pdf(self) -> None:
        self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()

    def when_the_peak_chat_finishes(self) -> None:
        if self.peak_chat_client is not None:
            self.peak_chat_client.join()

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
        self.probe.release_indexing()
        self.neighbour_ready = self._until_ready(self.neighbour_token, self.neighbour_id)

    def then_the_neighbour_document_is_ready(self) -> None:
        assert self.neighbour_ready.status_code == 200
        assert self.neighbour_ready.body == self._neighbour_ready(self.neighbour_id)

    def then_the_neighbour_text_is_indexed(self) -> None:
        assert self.probe.pieces_for(self.neighbour_id) == (NEIGHBOUR_TEXT,)

    def when_the_person_submits_a_pdf_of(self, size_bytes: int) -> None:
        self.edge_size = size_bytes
        self.edge_pdf = _pdf_of_size(size_bytes)
        self.upload = self.documents.submit_pdf(self.token, EDGE_NAME, self.edge_pdf)

    def then_the_document_is_accepted_at_that_size(self) -> None:
        assert self.upload.status_code == 201
        assert self.upload.body == self._document(
            self.upload.body["id"], EDGE_NAME, self.edge_size, None, None, "waiting"
        )

    def then_the_stored_size_is_that_byte_count(self) -> None:
        stored = self.probe.file_for(self.upload.body["id"])
        assert stored is not None
        assert len(stored) == self.edge_size

    def when_the_person_reads_the_document(self) -> None:
        self.read_back = self.documents.read(self.token, self.upload.body["id"])

    def then_the_size_the_person_reads_back_is_that_byte_count(self) -> None:
        assert self.read_back.status_code == 200
        assert self.read_back.body["size_bytes"] == self.edge_size

    def when_the_person_submits_a_pdf_that_is_costly_to_read_but_within_the_size_limit(self) -> None:
        self.pathological_pdf = _pad_pdf_to_minimum(self.lecture)
        self.probe.block_pdf_read()
        self.upload = self.documents.submit_pdf(self.token, PATHOLOGICAL_NAME, self.pathological_pdf)
        assert self.upload.status_code == 201
        self.probe.release_indexing()

    def then_indexing_finishes_or_fails_within_five_minutes(self) -> None:
        document_id = self.upload.body["id"]
        indexing = self._until_status(self.token, document_id, "indexing")
        assert indexing.status_code == 200
        assert indexing.body["status"] == "indexing"
        self.clock.advance(INDEXING_LIMIT_SECONDS)
        self.finished = self._until_terminal(self.token, document_id)
        assert self.finished.status_code == 200
        assert self.finished.body["status"] in {"ready", "failed"}

    def then_it_does_not_keep_running_after_that(self) -> None:
        document_id = self.upload.body["id"]
        terminal_status = self.finished.body["status"]
        piece_writes = self.probe.piece_write_count(document_id)
        self.clock.advance(60)
        self.probe.allow_pdf_read()
        time.sleep(0.5)
        after = self.documents.read(self.token, document_id)
        assert after.status_code == 200
        assert after.body["status"] == terminal_status
        assert self.probe.piece_write_count(document_id) == piece_writes

    def given_the_virus_check_clears_files(self) -> None:
        self.virus_scans_at_start = self.probe.virus_scans()

    def when_the_person_submits_a_valid_pdf(self) -> None:
        self.upload = self.documents.submit_pdf(self.token, LECTURE_NAME, self.lecture)

    def when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table(self) -> None:
        self.when_the_person_submits_a_valid_pdf()

    def given_the_standard_indexing_baseline(self) -> None:
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        self.standard_lecture = _pad_to_target_size(self.lecture, STANDARD_LECTURE_BYTES)

    def when_the_person_uploads_that_lecture(self) -> None:
        self.indexing_started_at = time.monotonic()
        self.upload = self.documents.submit_pdf(self.token, LECTURE_NAME, self.standard_lecture)
        assert self.upload.status_code == 201
        self.probe.release_indexing()

    def then_the_document_becomes_ready(self) -> None:
        self.ready = self._until_ready(
            self.token, self.upload.body["id"], seconds=INDEXING_CEILING_SECONDS
        )
        assert self.ready.status_code == 200
        assert self.ready.body["status"] == "ready"

    def then_indexing_finishes_within_the_indexing_ceiling(self) -> None:
        elapsed = time.monotonic() - self.indexing_started_at
        assert elapsed <= INDEXING_CEILING_SECONDS

    def then_the_virus_check_cleared_the_upload(self) -> None:
        assert self.probe.virus_scans() == self.virus_scans_at_start + 1

    def then_its_text_can_be_searched(self) -> None:
        searchable = self.documents.searchable_pieces(self.token, self.upload.body["id"])
        assert searchable.status_code == 200
        assert searchable.body["pieces"] == [FIVE_HUNDRED, JOINED]

    def when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table(self) -> None:
        self.upload = self.documents.submit_pdf(self.token, LECTURE_NAME, self.lecture)

    def when_the_person_submits_a_valid_pdf_and_also_sends_server_fields(self) -> None:
        self.upload = self.documents.submit_pdf_with_extra_fields(
            self.token,
            LECTURE_NAME,
            self.lecture,
            {
                "id": HOSTILE_DOCUMENT_ID,
                "owner": HOSTILE_OWNER_ID,
                "status": HOSTILE_STATUS,
                "page_count": HOSTILE_PAGE_COUNT,
                "piece_count": HOSTILE_PIECE_COUNT,
                "error": HOSTILE_ERROR,
                "size_bytes": HOSTILE_SIZE_BYTES,
                "created_at": HOSTILE_UPLOAD_TIME,
            },
        )

    def then_the_document_is_accepted_and_server_fields_stay_untouched(self) -> None:
        assert self.upload.status_code == 201
        document_id = self.upload.body["id"]
        assert document_id != HOSTILE_DOCUMENT_ID
        assert self.probe.document_owner(document_id) == self._account_id_from_token(self.token)
        assert self.upload.body == self._waiting(document_id)
        assert self.upload.body["page_count"] != int(HOSTILE_PAGE_COUNT)
        assert self.upload.body["piece_count"] != int(HOSTILE_PIECE_COUNT)
        assert self.upload.body["size_bytes"] == len(self.lecture)
        assert self.upload.body["size_bytes"] != int(HOSTILE_SIZE_BYTES)
        self.read_back = self.documents.read(self.token, document_id)
        assert self.read_back.status_code == 200
        assert self.read_back.body == self._waiting(document_id)
        assert "created_at" not in self.read_back.body

    def when_the_person_submits_a_pdf_that_would_store_more_than_2000_pieces(self) -> None:
        self.upload = self.documents.submit_pdf(
            self.token, MANY_PIECES_NAME, _pad_pdf_to_minimum(self.many_pieces)
        )
        assert self.upload.status_code == 201

    def when_the_many_pieces_document_finishes_indexing(self) -> None:
        self.probe.release_indexing()
        self.finished = self._until_terminal(self.token, self.upload.body["id"], seconds=300)

    def then_the_over_limit_document_is_failed(self) -> None:
        assert self.upload.status_code == 201
        assert self.finished.status_code == 200
        assert self.finished.body["status"] == "failed"

    def then_the_upload_is_answered_before_indexing_finishes(self) -> None:
        assert self.upload.status_code == 201
        assert self.upload.body == self._waiting(self.upload.body["id"])

    def when_the_person_reads_the_upload(self) -> None:
        self.read_back = self.documents.read(self.token, self.upload.body["id"])

    def when_the_person_lists_documents(self) -> None:
        self.listed = self.documents.list_documents(self.token)

    def given_the_person_owns_more_than_one_page_of_documents(self) -> None:
        self.probe.hold_indexing()
        needed = PAGE_SIZE + 1
        for index in range(needed):
            if index > 0 and index % 5 == 0:
                self.clock.advance(60)
            submitted = self.documents.submit_pdf(
                self.token, f"library-{index:03d}.pdf", self.neighbour_pdf
            )
            assert submitted.status_code == 201
            self.person_upload_ids.append(submitted.body["id"])

    def when_the_person_has_read_the_first_page(self) -> None:
        self.first_page = self.documents.list_documents(self.token, page=1)
        assert self.first_page.status_code == 200
        assert self.first_page.body["has_next"] is True
        assert len(self.first_page.body["documents"]) == PAGE_SIZE

    def when_a_new_document_sorts_into_that_page(self) -> None:
        if len(self.person_upload_ids) % 5 == 0:
            self.clock.advance(60)
        self.upload = self.documents.submit_pdf(self.token, "newest-arrival.pdf", self.lecture)
        assert self.upload.status_code == 201
        self.person_upload_ids.append(self.upload.body["id"])

    def then_each_document_appears_once_across_the_two_pages(self) -> None:
        first_ids = [document["id"] for document in self.first_page.body["documents"]]
        next_ids = [document["id"] for document in self.next_page.body["documents"]]
        combined = first_ids + next_ids
        arrived = self.upload.body["id"]
        before_arrival = set(self.person_upload_ids) - {arrived}
        assert len(combined) == len(set(combined))
        assert set(combined) == before_arrival
        assert arrived not in next_ids
        assert len(self.person_upload_ids) == PAGE_SIZE + 2

    def when_two_documents_are_uploaded_at_the_same_instant(self) -> None:
        self.clock.advance(60)
        with ThreadPoolExecutor(max_workers=2) as pool:
            left = pool.submit(
                self.documents.submit_pdf, self.token, "pair-left.pdf", self.neighbour_pdf
            )
            right = pool.submit(
                self.documents.submit_pdf, self.token, "pair-right.pdf", self.neighbour_pdf
            )
            left_result = left.result()
            right_result = right.result()
        assert left_result.status_code == 201
        assert right_result.status_code == 201
        self.pair_ids = [left_result.body["id"], right_result.body["id"]]

    def when_the_person_reads_the_first_page_again(self) -> None:
        first = self.documents.list_documents(self.token, page=1)
        second = self.documents.list_documents(self.token, page=1)
        assert first.status_code == 200
        assert second.status_code == 200
        self.first_page_order = [document["id"] for document in first.body["documents"]]
        self.second_page_order = [document["id"] for document in second.body["documents"]]

    def then_two_documents_uploaded_at_the_same_instant_keep_the_same_order(self) -> None:
        for order in (self.first_page_order, self.second_page_order):
            pair = [document_id for document_id in order if document_id in self.pair_ids]
            assert pair == [self.pair_ids[0], self.pair_ids[1]] or pair == [
                self.pair_ids[1],
                self.pair_ids[0],
            ]
        assert self.first_page_order[:2] == self.second_page_order[:2]

    def given_a_signed_in_person_with_more_documents_than_one_page(self) -> None:
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        content = self.neighbour_pdf
        for index in range(PAGE_SIZE + 1):
            if index > 0 and index % 5 == 0:
                self.clock.advance(61)
            uploaded = self.documents.submit_pdf(self.token, f"page-{index:03d}.pdf", content)
            assert uploaded.status_code == 201
            self.person_upload_ids.append(uploaded.body["id"])

    def given_a_neighbour_with_a_document_of_their_own(self) -> None:
        self.given_a_neighbour_account()
        self.then_the_neighbour_is_signed_in()
        self.when_the_neighbour_submits_a_pdf()
        self.then_the_neighbour_upload_is_waiting()

    def given_a_signed_in_person_and_a_neighbour_with_a_document(self) -> None:
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        self.when_the_person_submits_a_valid_pdf()
        assert self.upload.status_code == 201
        self.given_a_neighbour_with_a_document_of_their_own()

    def when_the_person_opens_the_neighbours_document(self) -> None:
        self.neighbour_refusal = self.documents.read(self.token, self.neighbour_id)

    def when_the_person_opens_a_document_that_does_not_exist(self) -> None:
        self.missing_refusal = self.documents.read(self.token, str(uuid4()))

    def when_a_guest_opens_the_persons_document(self) -> None:
        self.guest_refusal = self.documents.read_as_guest(self.upload.body["id"])

    def then_each_refusal_is_the_same_status_and_the_same_body(self) -> None:
        refusals = (self.neighbour_refusal, self.missing_refusal, self.guest_refusal)
        for refusal in refusals:
            assert refusal.status_code == 404
            assert refusal.body == DOCUMENT_NOT_FOUND

    def then_none_of_them_includes_the_documents_name_or_text(self) -> None:
        forbidden = (NEIGHBOUR_NAME, LECTURE_NAME, NEIGHBOUR_TEXT, EXTRACTED, JOINED, FIVE_HUNDRED)
        refusals = (self.neighbour_refusal, self.missing_refusal, self.guest_refusal)
        for refusal in refusals:
            payload = json.dumps(refusal.body)
            for fragment in forbidden:
                assert fragment not in payload

    def given_a_guest(self) -> None:
        self.intake_count_before_guest = len(self.probe._intake.rows)

    def when_a_missing_document_is_opened_without_the_screen(self) -> None:
        self.missing_refusal = self.documents.read_as_guest(str(uuid4()))

    def when_the_guest_reads_the_document_list_without_the_screen(self) -> None:
        self.guest_list_refusal = self.documents.list_as_guest()

    def when_the_guest_uploads_a_pdf_without_the_screen(self) -> None:
        self.guest_upload_refusal = self.documents.submit_pdf_as_guest(LECTURE_NAME, self.lecture)

    def then_each_guest_refusal_matches_a_missing_document(self) -> None:
        assert self.missing_refusal.status_code == 404
        assert self.missing_refusal.body == DOCUMENT_NOT_FOUND
        for refusal in (self.guest_list_refusal, self.guest_upload_refusal):
            assert refusal.status_code == self.missing_refusal.status_code
            assert refusal.body == self.missing_refusal.body

    def then_no_document_is_added(self) -> None:
        assert len(self.probe._intake.rows) == self.intake_count_before_guest

    def then_neither_guest_answer_includes_a_document_name_or_text(self) -> None:
        forbidden = (NEIGHBOUR_NAME, LECTURE_NAME, NEIGHBOUR_TEXT, EXTRACTED, JOINED, FIVE_HUNDRED)
        for refusal in (self.guest_list_refusal, self.guest_upload_refusal):
            payload = json.dumps(refusal.body)
            for fragment in forbidden:
                assert fragment not in payload

    def when_the_person_reads_the_first_page(self) -> None:
        self.first_page = self.documents.list_documents(self.token, page=1)

    def when_the_person_reads_the_next_page(self) -> None:
        self.next_page = self.documents.list_documents(self.token, page=2)
        assert self.next_page.status_code == 200

    def when_the_person_reads_the_next_page_from_the_first_page_cursor(self) -> None:
        last_id = self.first_page.body["documents"][-1]["id"]
        self.next_page = self.documents.list_documents(self.token, after=last_id)
        assert self.next_page.status_code == 200

    def then_the_page_holds_at_most_fifty_documents(self) -> None:
        assert self.first_page.status_code == 200
        documents = self.first_page.body["documents"]
        assert len(documents) <= PAGE_SIZE

    def then_the_newest_document_is_first(self) -> None:
        assert self.first_page.body["documents"][0]["id"] == self.person_upload_ids[-1]
        page_ids = [document["id"] for document in self.first_page.body["documents"]]
        assert page_ids == list(reversed(self.person_upload_ids[-PAGE_SIZE:]))

    def then_a_later_page_holds_the_rest(self) -> None:
        assert self.first_page.body["has_next"] is True
        assert self.next_page.status_code == 200
        assert self.next_page.body["has_next"] is False
        rest_ids = [document["id"] for document in self.next_page.body["documents"]]
        assert rest_ids == list(reversed(self.person_upload_ids[: len(self.person_upload_ids) - PAGE_SIZE]))

    def then_the_neighbours_document_is_absent(self) -> None:
        listed_ids = {
            document["id"]
            for document in self.first_page.body["documents"] + self.next_page.body["documents"]
        }
        assert self.neighbour_id not in listed_ids

    def then_the_list_is_empty(self) -> None:
        assert self.listed.status_code == 200
        assert self.listed.body == {"documents": [], "has_next": False}

    def given_a_signed_in_person_with_one_document(self) -> None:
        self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        assert self.upload.status_code == 201
        self.when_the_person_lists_documents()
        self.baseline_list = self.listed.body

    def when_the_person_submits_no_file(self) -> None:
        self.refusal = self.documents.submit_no_file(self.token)

    def when_the_person_submits_a_file_that_is_not_a_pdf(self) -> None:
        self.refusal = self.documents.submit_pdf(self.token, "notes.pdf", self.not_pdf)

    def when_the_person_submits_a_pdf_with_no_text(self) -> None:
        self.refusal = self.documents.submit_pdf(self.token, "blank.pdf", self.empty_pdf)

    def when_the_person_submits_a_pdf_one_byte_under_the_minimum(self) -> None:
        self.refusal = self.documents.submit_pdf(self.token, "small.pdf", self.under_min)

    def when_the_person_submits_a_pdf_one_byte_over_the_maximum(self) -> None:
        self.refusal = self.documents.submit_pdf(self.token, "large.pdf", self.over_max)

    def when_the_person_submits_an_encrypted_pdf(self) -> None:
        self.refusal = self.documents.submit_pdf(self.token, "locked.pdf", self.encrypted_pdf)

    def when_the_person_submits_a_pdf_with_no_file_name(self) -> None:
        self.refusal = self.documents.submit_upload(
            self.token,
            {"file": ("", _pdf_of_size(MIN_BYTES), "application/pdf")},
        )

    def when_the_person_submits_a_pdf_whose_name_is_256_characters(self) -> None:
        self.refusal = self.documents.submit_pdf(self.token, OVERLONG_PDF_NAME, self.lecture)

    def given_the_virus_check(self, outcome: str) -> None:
        self.probe.set_virus_outcome(_VIRUS_OUTCOMES[outcome])

    def given_the_document_store_is_down(self) -> None:
        self.probe.set_document_store_down()

    def given_the_document_store_was_down_and_is_back(self) -> None:
        self.probe.set_document_store_down()
        self.probe.set_document_store_up()

    def then_the_upload_is_refused_as_store_unavailable(self) -> None:
        assert self.upload.status_code == 503
        assert self.upload.body == {
            "code": "unavailable",
            "message": "The account store is unreachable",
        }

    def then_no_document_is_stored(self) -> None:
        assert self.probe.stored_document_ids() == frozenset()
        assert self.probe.piece_document_ids() == frozenset()

    def then_the_document_is_not_marked_ready(self) -> None:
        assert all(status != "ready" for status in self.probe.document_statuses().values())

    def given_the_document_store_connection_baselines(self) -> None:
        self.baseline_connections = self.probe.document_store_live()
        self.baseline_file_handles = self.probe.open_file_handles()
        self.baseline_temp_files = self.probe.temporary_files()

    def when_several_uploads_fail_because_the_store_the_virus_check_or_the_search_store_is_unavailable(
        self,
    ) -> None:
        self.probe.set_document_store_down()
        store_refusal = self.documents.submit_pdf(self.token, "infra-store-down.pdf", self.lecture)
        assert store_refusal.status_code == 503
        self.probe.set_document_store_up()
        self.probe.prepare_virus_and_search_store_calls()
        self.probe.set_virus_call_reaches_its_deadline()
        virus_refusal = self.documents.submit_pdf(
            self.token, "infra-virus-down.pdf", self.lecture
        )
        assert virus_refusal.status_code == 400
        assert virus_refusal.body["code"] == "virus_detected"
        self.probe.prepare_virus_and_search_store_calls()
        self.probe.set_search_store_outcome("refuses")
        search_failure = self.documents.submit_pdf(
            self.token, "infra-search-down.pdf", self.lecture
        )
        assert search_failure.status_code == 201
        self.probe.release_indexing()
        finished = self._until_terminal(self.token, search_failure.body["id"])
        assert finished.status_code == 200
        assert finished.body["status"] == "failed"

    def then_the_open_connections_return_to_the_baseline(self) -> None:
        assert self.probe.document_store_live() == self.baseline_connections

    def then_the_open_file_handles_and_temporary_files_return_to_the_baseline(self) -> None:
        assert self.probe.open_file_handles() == self.baseline_file_handles
        assert self.probe.temporary_files() == self.baseline_temp_files

    def when_the_document_store_is_back(self) -> None:
        self.probe.set_document_store_up()
        self.probe.prepare_virus_and_search_store_calls()
        self.probe.set_search_store_outcome(None)

    def then_a_further_upload_can_still_be_accepted_once_the_store_is_back(self) -> None:
        self.when_the_person_submits_a_valid_pdf()
        assert self.upload.status_code == 201
        assert self.upload.body["status"] == "waiting"

    def when_the_person_submits_a_pdf(self) -> None:
        self.piece_ids_before_submit = self.probe.piece_document_ids()
        self.refusal = self.documents.submit_pdf(
            self.token, SECOND_PDF_NAME, _pad_pdf_to_minimum(self.neighbour_pdf)
        )

    def then_the_file_is_not_indexed(self) -> None:
        assert self.probe.piece_document_ids() == self.piece_ids_before_submit

    def then_the_upload_is_refused(self, refusal_key: str) -> None:
        code, message = REFUSALS[refusal_key]
        assert self.refusal.status_code == 400
        assert self.refusal.body == {"code": code, "message": message}

    def given_a_known_secret_and_a_phrase_that_appears_only_in_the_pdf(self) -> None:
        self.known_secret = DISCLOSURE_KNOWN_SECRET
        self.pdf_phrase = DISCLOSURE_PDF_PHRASE
        self.pdf_with_phrase = _pdf_with_embedded_phrase(self.pdf_phrase)
        self.not_pdf_with_phrase = _non_pdf_with_phrase(self.pdf_phrase)

    def when_an_upload_is_refused_for_the_pdf_with_the_phrase(self) -> None:
        if self.logs is not None:
            self.logs.clear()
        self.refusal = self.documents.submit_pdf(self.token, "bad.pdf", self.not_pdf_with_phrase)
        assert self.refusal.status_code == 400
        self._remember_disclosure_answer(self.refusal)

    def when_indexing_fails_for_the_pdf_with_the_phrase(self) -> None:
        if self.logs is not None:
            self.logs.clear()
        self.probe.hold_indexing()
        self.probe.set_search_store_outcome("refuses")
        uploaded = self.documents.submit_pdf(self.token, "index-fail.pdf", self.pdf_with_phrase)
        assert uploaded.status_code == 201
        document_id = uploaded.body["id"]
        self.probe.release_indexing()
        seen = self._until_terminal(self.token, document_id, seconds=15)
        self._remember_disclosure_answer(seen)

    def when_the_virus_check_rejects_the_pdf_with_the_phrase(self) -> None:
        if self.logs is not None:
            self.logs.clear()
        self.given_the_virus_check("finds a virus")
        self.refusal = self.documents.submit_pdf(self.token, "virus.pdf", self.pdf_with_phrase)
        assert self.refusal.status_code == 400
        self._remember_disclosure_answer(self.refusal)

    def when_the_upload_count_cannot_be_read_for_the_pdf_with_the_phrase(self) -> None:
        if self.logs is not None:
            self.logs.clear()
        assert self.rates is not None
        self.probe.set_virus_outcome("clears")
        self.probe.set_search_store_outcome(None)
        self.rates.fail_reads = True
        self.refusal = self.documents.submit_pdf(self.token, "rate.pdf", self.pdf_with_phrase)
        assert self.refusal.status_code == 429
        self._remember_disclosure_answer(self.refusal)

    def then_the_answer_and_the_log_do_not_contain_the_secret_the_phrase_a_stack_a_file_path_or_an_internal_name(
        self,
    ) -> None:
        log_text = "" if self.logs is None else self.logs.text()
        for blob in (self.disclosure_answer_text, log_text):
            assert self.known_secret not in blob
            assert self.pdf_phrase not in blob
            for marker in _DISCLOSURE_STACK_MARKERS:
                assert marker not in blob
            for marker in _DISCLOSURE_PATH_MARKERS:
                assert marker not in blob
            for marker in _DISCLOSURE_INTERNAL_MARKERS:
                assert marker not in blob

    def _remember_disclosure_answer(self, result: HttpResult) -> None:
        self.disclosure_answer_text = json.dumps(result.body) + str(result.status_code)

    def then_the_list_is_unchanged(self) -> None:
        self.when_the_person_lists_documents()
        assert self.listed.body == self.baseline_list

    def then_the_next_read_shows_waiting_not_a_stale_copy(self) -> None:
        uploaded = self.upload.body
        assert self.read_back.status_code == 200
        assert self.read_back.body == uploaded
        assert self.listed.status_code == 200
        assert self.listed.body == {"documents": [uploaded], "has_next": False}

    def given_an_accepted_document_whose_indexing_was_not_started(self) -> None:
        self.probe.hold_indexing()
        self.upload = self.documents.submit_pdf(self.token, LECTURE_NAME, self.lecture)
        assert self.upload.status_code == 201
        assert self.upload.body == self._waiting(self.upload.body["id"])
        self.read_back = self.documents.read(self.token, self.upload.body["id"])
        assert self.read_back.status_code == 200
        assert self.read_back.body["status"] == "waiting"

    def given_a_document_that_is(self, status: str) -> None:
        if status == "waiting":
            self.given_a_document_that_is_waiting()
            return
        if status == "indexing":
            self.given_a_document_that_is_indexing()
            return
        self.given_a_document_that_is_finished(status)
        self.document_id = self.finished.body["id"]
        self._snapshot_before_move()

    def given_a_document_that_is_waiting(self) -> None:
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        self.given_an_accepted_document_whose_indexing_was_not_started()
        self.document_id = self.upload.body["id"]
        self._snapshot_before_move()

    def given_a_document_that_is_indexing(self) -> None:
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        self.probe.block_pdf_read()
        self.probe.release_indexing()
        self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        self.document_id = self.upload.body["id"]
        indexing = self._until_status(self.token, self.document_id, "indexing")
        assert indexing.status_code == 200
        assert indexing.body["status"] == "indexing"
        self._snapshot_before_move()

    def _snapshot_before_move(self) -> None:
        self.pieces_before_move = self.probe.pieces_for(self.document_id)
        self.searchable_before_move = self.documents.searchable_pieces(self.token, self.document_id)
        self.file_before_move = self.probe.file_for(self.document_id)

    def when_the_document_is_moved_toward(self, toward: str) -> None:
        self.move_result = self.documents.move_indexing_status(self.token, self.document_id, toward)

    def then_the_move_is_refused(self) -> None:
        assert self.move_result.status_code == 409
        assert self.move_result.body["code"] == "invalid_status_transition"

    def then_the_document_stays(self, status: str) -> None:
        read = self.documents.read(self.token, self.document_id)
        assert read.status_code == 200
        assert read.body["status"] == status

    def then_the_document_stays_waiting(self) -> None:
        self.then_the_document_stays("waiting")

    def then_its_pieces_its_search_entries_and_its_file_are_untouched(self) -> None:
        assert self.probe.pieces_for(self.document_id) == self.pieces_before_move
        searchable = self.documents.searchable_pieces(self.token, self.document_id)
        assert searchable.status_code == 200
        assert searchable.body == self.searchable_before_move.body
        assert self.probe.file_for(self.document_id) == self.file_before_move

    def given_an_accepted_document(self) -> None:
        self.probe.prepare_virus_and_search_store_calls()
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        self.probe.hold_indexing()
        self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        self.then_the_upload_is_answered_before_indexing_finishes()

    def and_the_embedding_call(self, outcome: str) -> None:
        mapped = {
            "refuses": "refuses",
            "answers unreadable": "unreadable",
            "fails as a server error": "server_error",
        }
        self.probe.set_embedding_outcome(mapped[outcome])
        self.embedding_outcome = outcome

    def when_indexing_runs(self) -> None:
        self.probe.release_indexing()
        self.finished = self._until_terminal(self.token, self.upload.body["id"])

    def then_the_document_is_failed_and_not_retried_for_that_refusal(self) -> None:
        document_id = self.upload.body["id"]
        assert self.finished.status_code == 200
        assert self.finished.body["status"] == "failed"
        attempts_after_finish = self.probe.indexing_attempts(document_id)
        self.clock.advance(120)
        time.sleep(0.3)
        later = self.documents.read(self.token, document_id)
        assert later.status_code == 200
        assert later.body["status"] == "failed"
        assert self.probe.indexing_attempts(document_id) == attempts_after_finish

    def then_the_document_is_failed_after_unreadable_embedding(self) -> None:
        assert self.finished.status_code == 200
        assert self.finished.body["status"] == "failed"

    def then_the_server_error_try_counts_toward_the_three(self) -> None:
        document_id = self.upload.body["id"]
        assert self.finished.status_code == 200
        assert self.finished.body["status"] in {"waiting", "indexing"}
        assert self.probe.embedding_attempts(document_id) == 1

    def and_the_search_store(self, outcome: str) -> None:
        self.probe.set_search_store_outcome(outcome)

    def and_the_search_store_refuses(self) -> None:
        self.and_the_search_store("refuses")

    def given_a_virus_check_and_a_search_store_call(self) -> None:
        self.probe.prepare_virus_and_search_store_calls()

    def when_the_virus_check_finishes_just_before_its_deadline(self) -> None:
        self.probe.set_virus_call_finishes_just_before_its_deadline()

    def when_the_virus_check_reaches_its_deadline(self) -> None:
        self.probe.set_virus_call_reaches_its_deadline()

    def when_the_person_submits_a_pdf_for_virus_deadline_check(self) -> None:
        self.refusal = self.documents.submit_pdf(
            self.token, SECOND_PDF_NAME, _pad_pdf_to_minimum(self.neighbour_pdf)
        )
        self.upload = self.refusal

    def then_the_external_call_still_counts_as_answered_for_the_upload(self) -> None:
        assert self.upload.status_code == 201
        assert self.upload.body["status"] == "waiting"

    def when_the_search_store_call_finishes_just_before_its_deadline(self) -> None:
        self.probe.prepare_virus_and_search_store_calls()
        self.probe.set_search_store_call_finishes_just_before_its_deadline()

    def when_the_search_store_call_reaches_its_deadline(self) -> None:
        self.probe.prepare_virus_and_search_store_calls()
        self.probe.set_search_store_call_reaches_its_deadline()

    def then_the_external_call_still_counts_as_answered_for_indexing(self) -> None:
        assert self.finished.status_code == 200
        assert self.finished.body["status"] == "ready"

    def then_the_search_store_fails_the_document(self) -> None:
        self.then_the_document_is_failed_after_indexing()
        self.then_nothing_from_the_file_can_be_searched()

    def then_the_finished_document_is_not_ready(self) -> None:
        assert self.finished.status_code == 200
        assert self.finished.body["status"] != "ready"

    def then_the_document_is_failed_after_indexing(self) -> None:
        assert self.finished.status_code == 200
        assert self.finished.body["status"] == "failed"

    def then_the_failure_is_visible_on_the_document(self) -> None:
        assert self.finished.status_code == 200
        assert self.finished.body["status"] == "failed"
        assert self.finished.body["error"] is not None
        assert self.finished.body["error"] != ""

    def when_the_document_is_given_a_status_that_is_not_waiting_indexing_ready_or_failed(self) -> None:
        document_id = self.upload.body["id"]
        self.probe.seed_pieces(document_id, (FIVE_HUNDRED,), EXTRACTED)
        self.probe.force_document_status(document_id, UNKNOWN_STATUS)
        self.read_back = self.documents.read(self.token, document_id)

    def then_the_document_is_not_ready(self) -> None:
        assert self.read_back.status_code == 200
        assert self.read_back.body["status"] == UNKNOWN_STATUS
        assert self.read_back.body["status"] != "ready"

    def then_nothing_from_the_file_is_newly_searchable(self) -> None:
        document_id = self.upload.body["id"]
        self.searchable = self.documents.searchable_pieces(self.token, document_id)
        assert self.searchable.status_code == 200
        assert self.searchable.body["pieces"] == []

    def when_two_indexing_claims_pass_the_status_check_together(self) -> None:
        self.probe.arm_dual_claim_sync()
        try:
            self.probe.trigger_dual_claim_race()
        finally:
            self.probe.disarm_dual_claim_sync()
        self.probe.release_indexing()
        self.ready = self._until_ready(self.token, self.upload.body["id"])

    def given_indexing_of_a_document_is_still_running(self) -> None:
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        self.probe.hold_indexing()
        self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        self.probe.block_pdf_read()
        self.probe.release_indexing()
        document_id = self.upload.body["id"]
        indexing = self._until_status(self.token, document_id, "indexing")
        assert indexing.status_code == 200
        assert indexing.body["status"] == "indexing"

    def when_a_second_indexing_run_starts_for_that_document(self) -> None:
        document_id = self.upload.body["id"]
        self._second_index_thread = threading.Thread(
            target=self.probe.trigger_second_indexing_run,
            args=(document_id,),
            daemon=True,
        )
        self._second_index_thread.start()
        time.sleep(0.2)

    def given_a_document_loaded_twice_while_it_is_indexing(self) -> None:
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        self.probe.block_pdf_read()
        self.probe.release_indexing()
        self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        document_id = self.upload.body["id"]
        indexing = self._until_status(self.token, document_id, "indexing")
        assert indexing.status_code == 200
        assert indexing.body["status"] == "indexing"
        self.probe.hold_two_loads(document_id)

    def when_one_save_marks_it_ready_and_the_other_marks_it_failed(self) -> None:
        document_id = self.upload.body["id"]
        self.probe.seed_pieces(document_id, (FIVE_HUNDRED, JOINED), EXTRACTED)
        self.ready_save = self.documents.stale_save_from_load(
            self.token, document_id, 0, "ready"
        )
        self.failed_save = self.documents.stale_save_from_load(
            self.token, document_id, 1, "failed"
        )
        self.final_read = self.documents.read(self.token, document_id)

    def then_the_later_save_does_not_silently_discard_the_earlier_one(self) -> None:
        assert self.ready_save.status_code == 200
        assert self.failed_save.status_code == 200
        assert self.final_read.status_code == 200
        assert self.final_read.body["status"] == "ready"

    def then_the_document_ends_in_exactly_one_of_those_statuses(self) -> None:
        assert self.final_read.body["status"] in {"ready", "failed"}

    def then_the_pieces_match_that_status(self) -> None:
        document_id = self.upload.body["id"]
        status = self.final_read.body["status"]
        searchable = self.documents.searchable_pieces(self.token, document_id)
        assert searchable.status_code == 200
        if status == "ready":
            assert searchable.body["pieces"] == [FIVE_HUNDRED, JOINED]
            self._assert_lecture_pieces()
        else:
            assert searchable.body["pieces"] == []
            assert self.probe.pieces_for(document_id) == ()

    def then_the_two_runs_do_not_both_write_pieces(self) -> None:
        document_id = self.upload.body["id"]
        self.probe.allow_pdf_read()
        self.ready = self._until_ready(self.token, document_id)
        self._second_index_thread.join(timeout=30)
        assert self.probe.indexing_attempts(document_id) == 1
        assert self.probe.piece_write_count(document_id) == 1

    def then_one_set_of_pieces_exists(self) -> None:
        assert self.ready.status_code == 200
        assert self.ready.body == self._ready(self.upload.body["id"])
        self._assert_lecture_pieces()

    def then_one_claim_proceeds(self) -> None:
        document_id = self.upload.body["id"]
        assert self.probe.piece_write_count(document_id) == 1

    def then_one_set_of_pieces_is_stored(self) -> None:
        self._assert_lecture_pieces()
        assert self.ready.status_code == 200
        assert self.ready.body["piece_count"] == PIECE_COUNT

    def when_indexing_is_due(self) -> None:
        self.probe.release_indexing()

    def given_a_document_whose_indexing_fails_every_time(self) -> None:
        self.probe.hold_indexing()
        submitted = self.documents.submit_pdf(self.token, "always-fails.pdf", self.neighbour_pdf)
        assert submitted.status_code == 201
        self.failing_id = submitted.body["id"]
        self.probe.mark_indexing_always_fails(self.failing_id)

    def and_a_later_valid_document(self) -> None:
        submitted = self.documents.submit_pdf(self.token, LECTURE_NAME, self.lecture)
        assert submitted.status_code == 201
        self.later_id = submitted.body["id"]

    def when_indexing_has_been_tried_three_times(self) -> None:
        self.probe.release_indexing()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if self.probe.indexing_attempts(self.failing_id) >= 3:
                break
            time.sleep(0.05)
        assert self.probe.indexing_attempts(self.failing_id) >= 3
        self.failing_final = self._until_terminal(self.token, self.failing_id)
        self.later_final = self._until_terminal(self.token, self.later_id)

    def then_the_failing_document_is_failed(self) -> None:
        assert self.failing_final.status_code == 200
        assert self.failing_final.body["status"] == "failed"

    def then_the_later_document_still_becomes_ready(self) -> None:
        assert self.later_final.status_code == 200
        assert self.later_final.body == self._ready(self.later_id)

    def then_the_document_becomes_ready_or_failed_and_does_not_stay_waiting(self) -> None:
        self.ready = self._until_ready(self.token, self.upload.body["id"])
        assert self.ready.status_code == 200
        assert self.ready.body["status"] in {"ready", "failed"}
        assert self.ready.body["status"] != "waiting"

    def given_an_accepted_document_that_is_still_indexing(self) -> None:
        self.probe.block_pdf_read()
        self.probe.release_indexing()
        self.upload = self.documents.submit_pdf(self.token, LECTURE_NAME, self.lecture)
        assert self.upload.status_code == 201
        assert self.upload.body == self._waiting(self.upload.body["id"])
        document_id = self.upload.body["id"]
        indexing = self._until_status(self.token, document_id, "indexing")
        assert indexing.status_code == 200
        assert indexing.body["status"] == "indexing"
        self.indexing_started_at = self.clock.now()

    def when_the_clock_is_just_short_of_five_minutes(self) -> None:
        elapsed = (self.clock.now() - self.indexing_started_at).total_seconds()
        remaining = INDEXING_LIMIT_SECONDS - 1 - elapsed
        assert remaining > 0
        self.clock.advance(int(remaining))

    def then_the_document_is_still_indexing(self) -> None:
        self.short_of_five = self.documents.read(self.token, self.upload.body["id"])
        assert self.short_of_five.status_code == 200
        assert self.short_of_five.body["status"] == "indexing"

    def when_five_minutes_have_passed(self) -> None:
        self.clock.advance(1)
        self.after_five = self._until_ready(self.token, self.upload.body["id"])

    def then_the_document_is_failed_after_five_minutes(self) -> None:
        assert self.after_five.status_code == 200
        assert self.after_five.body["status"] == "failed"

    def then_in_flight_indexing_is_cancelled(self) -> None:
        document_id = self.upload.body["id"]
        self.probe.allow_pdf_read()
        time.sleep(0.5)
        assert self.probe.piece_write_count(document_id) == 0

    def then_nothing_is_stored_after_that_instant(self) -> None:
        document_id = self.upload.body["id"]
        assert self.probe.pieces_for(document_id) == ()
        assert self.probe.extracted_text(document_id) == ""

    def when_the_document_finishes_indexing(self) -> None:
        self.probe.release_indexing()
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

    def then_the_neighbours_file_is_already_gone(self) -> None:
        assert self.probe.file_for(self.neighbour_id) is None

    def when_indexing_fails_on_one_table_after_an_earlier_step_succeeded(self) -> None:
        self.probe.fail_table_after_text_step()
        self.upload = self.documents.submit_pdf(self.token, LECTURE_NAME, self.lecture)
        assert self.upload.status_code == 201
        self.probe.release_indexing()
        self.finished = self._until_ready(self.token, self.upload.body["id"])

    def then_the_document_is_failed(self) -> None:
        assert self.finished.status_code == 200
        assert self.finished.body == self._failed(self.upload.body["id"])

    def then_the_failure_names_that_table(self) -> None:
        assert self.finished.body["error"] == TABLE_NAMED

    def then_nothing_from_the_file_can_be_searched(self) -> None:
        document_id = self.upload.body["id"]
        assert self.probe.pieces_for(document_id) == ()
        assert self.probe.extracted_text(document_id) == ""

    def then_no_piece_rows_remain(self) -> None:
        assert self.probe.piece_write_count(self.upload.body["id"]) == 0

    def then_the_neighbours_document_and_file_are_unchanged(self) -> None:
        assert self.neighbour_ready.body == self._neighbour_ready(self.neighbour_id)
        assert self.probe.pieces_for(self.neighbour_id) == (NEIGHBOUR_TEXT,)
        assert self.probe.file_for(self.neighbour_id) is None

    def given_a_document_that_is_finished(self, finished: str) -> None:
        self.expected_finished_status = finished
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        if finished == "ready":
            self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
            self.when_the_document_finishes_indexing()
            self.finished = self.ready
        else:
            self.when_indexing_fails_on_one_table_after_an_earlier_step_succeeded()
            assert self.finished.body["status"] == "failed"

    def when_indexing_is_requested_again_for_that_document(self) -> None:
        document_id = self.finished.body["id"]
        self.pieces_before_second_index_request = self.probe.piece_write_count(document_id)
        self.probe.trigger_second_indexing_run(document_id)
        time.sleep(0.2)
        self.finished = self.documents.read(self.token, document_id)

    def then_the_document_stays_finished(self) -> None:
        assert self.finished.status_code == 200
        if self.expected_finished_status == "ready":
            assert self.finished.body == self._ready(self.finished.body["id"])
        else:
            assert self.finished.body == self._failed(self.finished.body["id"])

    def then_no_second_set_of_pieces_is_stored(self) -> None:
        document_id = self.finished.body["id"]
        assert self.probe.piece_write_count(document_id) == self.pieces_before_second_index_request

    def given_indexing_wrote_the_pieces_and_then_failed_before_recording_ready(self) -> None:
        self.given_a_signed_in_person()
        self.then_the_person_is_signed_in()
        self.probe.fail_ready_save_after_pieces_once()
        self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        document_id = self.upload.body["id"]
        self.probe.release_indexing()
        indexing = self._until_status(self.token, document_id, "indexing")
        assert indexing.status_code == 200
        deadline = time.monotonic() + 30
        while time.monotonic() <= deadline:
            if self.probe.piece_write_count(document_id) >= 1:
                break
            time.sleep(0.05)
        assert self.probe.piece_write_count(document_id) == 1
        self.partial_read = self.documents.read(self.token, document_id)
        assert self.partial_read.status_code == 200
        assert self.partial_read.body["status"] == "indexing"
        self.virus_scans_before_retry = self.probe.virus_scans()
        self.piece_writes_before_retry = self.probe.piece_write_count(document_id)

    def when_indexing_runs_again(self) -> None:
        self.probe.trigger_second_indexing_run(self.upload.body["id"])
        self.ready = self._until_ready(self.token, self.upload.body["id"])

    def then_it_is_not_ready_while_the_pieces_are_incomplete(self) -> None:
        assert self.partial_read.body["status"] != "ready"
        assert self.probe.pieces_for(self.upload.body["id"]) != ()
        assert self.partial_read.body["piece_count"] is None

    def when_indexing_is_retried(self) -> None:
        self.virus_scans_before_retry = self.probe.virus_scans()
        self.piece_writes_before_retry = self.probe.piece_write_count(self.upload.body["id"])
        self.probe.release_indexing()
        self.finished = self._until_ready(self.token, self.upload.body["id"])

    def then_a_retry_does_not_run_the_virus_check_again(self) -> None:
        assert self.probe.virus_scans() == self.virus_scans_before_retry

    def then_a_retry_does_not_add_a_second_set_of_pieces(self) -> None:
        assert self.probe.piece_write_count(self.upload.body["id"]) == self.piece_writes_before_retry

    def given_many_accepted_documents(self) -> None:
        self.probe.hold_indexing()
        self.batch_document_ids = []
        for index in range(BATCH_RETRY_DOCUMENT_COUNT):
            submitted = self.documents.submit_pdf(
                self.token, f"batch-retry-{index}.pdf", self.neighbour_pdf
            )
            assert submitted.status_code == 201
            assert submitted.body["status"] == "waiting"
            self.batch_document_ids.append(submitted.body["id"])

    def and_the_search_store_fails_once_for_all_of_them(self) -> None:
        self.probe.arm_search_store_fails_once_for_all()

    def when_they_retry(self) -> None:
        self.probe.release_indexing()
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if all(
                self.probe.indexing_attempts(document_id) >= 2
                for document_id in self.batch_document_ids
            ):
                break
            time.sleep(0.05)

    def then_the_retries_are_not_all_issued_at_the_same_instant(self) -> None:
        retry_starts: list[float] = []
        for document_id in self.batch_document_ids:
            attempts = self.probe.indexing_attempt_times(document_id)
            assert len(attempts) >= 2, (
                f"document {document_id} expected a retry, got {len(attempts)} attempts"
            )
            retry_starts.append(attempts[1])
        spread = max(retry_starts) - min(retry_starts)
        assert spread > 0.0, "all retries were issued at the same instant"

    def then_none_of_them_is_tried_more_than_three_times(self) -> None:
        for document_id in self.batch_document_ids:
            assert self.probe.indexing_attempts(document_id) <= 3

    def when_the_person_submits_a_pdf_whose_name_is_255_characters_with_letters_outside_ascii(self) -> None:
        self.canonical_submitted_name = unicodedata.normalize("NFC", LONG_PDF_NAME)
        self.upload = self.documents.submit_pdf(self.token, LONG_PDF_NAME, self.lecture)

    def then_the_document_is_accepted(self) -> None:
        assert self.upload.status_code == 201
        assert self.upload.body["status"] == "waiting"
        self.stored_name = self.upload.body["name"]

    def then_the_stored_name_equals_the_submitted_name_after_canonical_composition(self) -> None:
        assert self.stored_name == self.canonical_submitted_name

    def when_the_person_reads_the_uploaded_document(self) -> None:
        self.read_back = self.documents.read(self.token, self.upload.body["id"])

    def then_the_name_read_back_equals_the_stored_name(self) -> None:
        assert self.read_back.status_code == 200
        assert self.read_back.body["name"] == self.stored_name

    def then_the_person_can_read_it_back(self) -> None:
        assert self.read_back.status_code == 200
        assert self.read_back.body == self.upload.body

    def when_the_person_uploads_a_pdf_whose_name_contains_query_metacharacters_and_markup(self) -> None:
        self.probe.fail_table_after_text_step()
        self.hostile_submitted_name = HOSTILE_NAME
        self.upload = self.documents.submit_pdf(
            self.token, HOSTILE_NAME, self.hostile_query_pdf
        )
        assert self.upload.status_code == 201
        self.stored_name = self.upload.body["name"]

    def when_a_failed_documents_reason_contains_the_same(self) -> None:
        self.probe.release_indexing()
        self.finished = self._until_terminal(self.token, self.upload.body["id"])

    def then_the_stored_name_equals_the_submitted_name(self) -> None:
        assert self.stored_name == self.hostile_submitted_name

    def then_the_list_shows_that_name_as_text(self) -> None:
        assert self.listed.status_code == 200
        listed = next(
            document
            for document in self.listed.body["documents"]
            if document["id"] == self.upload.body["id"]
        )
        assert listed["name"] == self.hostile_submitted_name

    def then_the_failure_reason_is_shown_as_text(self) -> None:
        assert self.finished.status_code == 200
        assert self.finished.body["error"] == HOSTILE_FAILURE_REASON

    def then_the_markup_is_not_treated_as_a_control(self) -> None:
        assert "<script>" in self.stored_name
        assert "<script>" in self.finished.body["error"]

    def then_the_query_metacharacters_are_not_treated_as_a_command(self) -> None:
        assert HOSTILE_MARKUP in self.stored_name
        assert HOSTILE_MARKUP in self.finished.body["error"]

    def then_the_neighbours_documents_are_unchanged(self) -> None:
        assert self.neighbour_ready.body == self._neighbour_ready(self.neighbour_id)
        assert self.probe.pieces_for(self.neighbour_id) == (NEIGHBOUR_TEXT,)

    def then_a_line_break_in_the_name_stays_inside_that_one_field(self) -> None:
        assert "\n" in self.stored_name
        assert self.read_back.body["name"] == self.hostile_submitted_name

    def then_query_metacharacters_in_the_pdf_text_are_not_a_command(self) -> None:
        document_id = self.upload.body["id"]
        extracted = self.probe.extracted_text(document_id)
        assert HOSTILE_PDF_TEXT in extracted

    def when_the_person_submits_a_pdf_whose_255th_place_falls_inside_one_letter(self) -> None:
        self.split_letter_submitted_name = SPLIT_LETTER_PDF_NAME
        self.upload = self.documents.submit_pdf(
            self.token, self.split_letter_submitted_name, self.lecture
        )

    def then_the_stored_name_contains_no_broken_letter(self) -> None:
        assert self.stored_name != NAIVE_BROKEN_NAME

    def then_the_stored_name_contains_no_replacement_character(self) -> None:
        assert "\ufffd" not in self.stored_name

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

    def _account_id_from_token(self, token: str) -> str:
        payload = jwt.decode(token, _ACCESS_SECRET, algorithms=["HS256"])
        return payload["sub"]

    def _waiting(self, document_id: str) -> dict:
        return self._document(document_id, LECTURE_NAME, len(self.lecture), None, None, "waiting")

    def _neighbour_waiting(self, document_id: str) -> dict:
        return self._document(document_id, NEIGHBOUR_NAME, len(self.neighbour_pdf), None, None, "waiting")

    def _ready(self, document_id: str) -> dict:
        return self._document(document_id, LECTURE_NAME, len(self.lecture), PAGE_COUNT, PIECE_COUNT, "ready")

    def _failed(self, document_id: str) -> dict:
        return self._document(document_id, LECTURE_NAME, len(self.lecture), None, None, "failed", TABLE_NAMED)

    def _neighbour_ready(self, document_id: str) -> dict:
        return self._document(
            document_id, NEIGHBOUR_NAME, len(self.neighbour_pdf), PAGE_COUNT, NEIGHBOUR_PIECE_COUNT, "ready"
        )

    def _document(
        self, document_id: str, name: str, size_bytes: int, page_count, piece_count, status: str, error=None
    ) -> dict:
        return {
            "id": document_id,
            "name": name,
            "size_bytes": size_bytes,
            "page_count": page_count,
            "piece_count": piece_count,
            "status": status,
            "error": error,
        }

    def _until_ready(self, token: str, document_id: str, seconds: int = 30):
        return self._until_terminal(token, document_id, seconds)

    def _until_status(self, token: str, document_id: str, status: str):
        deadline = time.monotonic() + 30
        seen = None
        while time.monotonic() <= deadline:
            seen = self.documents.read(token, document_id)
            if seen.status_code == 200 and seen.body["status"] == status:
                break
            time.sleep(0.05)
        return seen

    def _until_terminal(self, token: str, document_id: str, seconds: int = 30):
        deadline = time.monotonic() + seconds
        seen = None
        while time.monotonic() <= deadline:
            seen = self.documents.read(token, document_id)
            if seen.status_code == 200 and seen.body["status"] in {"ready", "failed"}:
                break
            time.sleep(0.05)
        return seen


def _pad_to_target_size(content: bytes, target_bytes: int) -> bytes:
    if len(content) > target_bytes:
        raise ValueError(target_bytes)
    if len(content) == target_bytes:
        return content
    need = target_bytes - len(content)
    return content + b"\n%" + (b"0" * (need - 2))


def _pad_pdf_to_minimum(content: bytes) -> bytes:
    if len(content) >= MIN_BYTES:
        return content
    need = MIN_BYTES - len(content)
    return content + b"\n%" + (b"0" * (need - 2))


def _pdf_of_size(size_bytes: int) -> bytes:
    minimum = len(_PDF_HEAD) + len(_PDF_TAIL)
    if size_bytes < minimum:
        raise ValueError(size_bytes)
    filler = size_bytes - minimum - 1
    return _PDF_HEAD + (b"%" + (b"0" * filler)) + _PDF_TAIL


def _pdf_with_embedded_phrase(phrase: str) -> bytes:
    raw = _PDF_HEAD + phrase.encode("utf-8") + b"\n" + _PDF_TAIL
    return _pad_pdf_to_minimum(raw)


def _non_pdf_with_phrase(phrase: str) -> bytes:
    prefix = b"PLAIN" + phrase.encode("utf-8")
    need = MIN_BYTES - len(prefix)
    return prefix + (b"x" * need)
