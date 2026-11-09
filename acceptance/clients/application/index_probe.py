import asyncio
import threading
import time
from dataclasses import replace
from uuid import UUID


class IndexProbe:
    def __init__(self):
        self._pieces: dict[str, tuple[str, ...]] = {}
        self._extracted: dict[str, str] = {}
        self._files: dict[str, bytes] = {}
        self._piece_write_counts: dict[str, int] = {}
        self._replace_counts: dict[str, int] = {}
        self._release = threading.Event()
        self._pdf_read_allowed = threading.Event()
        self._pdf_read_allowed.set()
        self._indexing_hold_seconds = 1.5
        self._fail_table_after_text = False
        self._fail_ready_after_pieces_once = False
        self._virus_scans = 0
        self._virus_outcome = "clears"
        self._indexing_always_fails: set[str] = set()
        self._indexing_attempts: dict[str, int] = {}
        self._indexing_attempt_times: dict[str, list[float]] = {}
        self._search_store_fail_once_armed = False
        self._search_store_fail_once_consumed = False
        self._search_store_outcome: str | None = None
        self._search_store_timeout_seconds = 0.05
        self._external_call_deadline_seconds = 0.12
        self._virus_call_delay: float | None = None
        self._search_store_call_delay: float | None = None
        self._embedding_outcome: str | None = None
        self._embedding_attempts: dict[str, int] = {}
        self._second_index_run = None
        self._dual_claim_race_run = None
        self._dual_claim_sync = False
        self._dual_claim_barrier: asyncio.Event | None = None
        self._dual_claim_arrivals = 0
        self._open_file_handles = 0
        self._temporary_files = 0

    def remember_file(self, document_id: str, content: bytes) -> None:
        self._files[document_id] = content

    def remove_file(self, document_id: str) -> None:
        self._files.pop(document_id, None)

    def file_for(self, document_id: str) -> bytes | None:
        return self._files.get(document_id)

    def replace_pieces(self, document_id: str, pieces: tuple[str, ...], extracted: str) -> None:
        self._pieces[document_id] = pieces
        self._extracted[document_id] = extracted
        self._replace_counts[document_id] = self._replace_counts.get(document_id, 0) + 1
        self._piece_write_counts[document_id] = self._piece_write_counts.get(document_id, 0) + 1

    def piece_write_count(self, document_id: str) -> int:
        return self._piece_write_counts.get(document_id, 0)

    def fail_table_after_text_step(self) -> None:
        self._fail_table_after_text = True

    def should_fail_table_after_text(self) -> bool:
        return self._fail_table_after_text

    def fail_ready_save_after_pieces_once(self) -> None:
        self._fail_ready_after_pieces_once = True

    def consume_fail_ready_after_pieces(self) -> bool:
        if not self._fail_ready_after_pieces_once:
            return False
        self._fail_ready_after_pieces_once = False
        return True

    def record_virus_scan(self) -> None:
        self._virus_scans += 1

    def virus_scans(self) -> int:
        return self._virus_scans

    def set_virus_outcome(self, outcome: str) -> None:
        self._virus_outcome = outcome

    def virus_outcome(self) -> str:
        return self._virus_outcome

    def piece_document_ids(self) -> frozenset[str]:
        return frozenset(self._pieces.keys())

    def pieces_for(self, document_id: str) -> tuple[str, ...]:
        return self._pieces.get(document_id, ())

    def extracted_text(self, document_id: str) -> str:
        return self._extracted.get(document_id, "")

    def remember_extracted(self, document_id: str, text: str) -> None:
        self._extracted[document_id] = text

    def release_indexing(self) -> None:
        self._release.set()

    def hold_indexing(self) -> None:
        self._release.clear()

    def indexing_hold_seconds(self) -> float:
        return self._indexing_hold_seconds

    def indexing_released(self) -> bool:
        return self._release.is_set()

    def wait_for_indexing_release(self, timeout: float) -> bool:
        return self._release.wait(timeout)

    def attach_intake(self, intake) -> None:
        self._intake = intake

    def attach_pieces(self, pieces) -> None:
        self._pieces_index = pieces

    def set_document_store_down(self) -> None:
        self._intake.dead = True

    def set_document_store_up(self) -> None:
        self._intake.dead = False

    def document_store_live(self) -> int:
        return self._intake.live

    def enter_pdf_read(self) -> None:
        self._open_file_handles += 1
        self._temporary_files += 1

    def exit_pdf_read(self) -> None:
        self._open_file_handles -= 1
        self._temporary_files -= 1

    def open_file_handles(self) -> int:
        return self._open_file_handles

    def temporary_files(self) -> int:
        return self._temporary_files

    def stored_document_ids(self) -> frozenset[str]:
        return frozenset(str(document_id) for document_id in self._intake.rows)

    def document_statuses(self) -> dict[str, str]:
        return {
            str(document_id): row[1].status for document_id, row in self._intake.rows.items()
        }

    def force_document_status(self, document_id: str, status: str) -> None:
        doc_id = UUID(document_id)
        row = self._intake.rows.get(doc_id)
        if row is None:
            raise KeyError(document_id)
        owner, document = row
        self._intake.rows[doc_id] = (owner, replace(document, status=status))

    def force_failed_document(self, document_id: str, reason: str) -> None:
        doc_id = UUID(document_id)
        row = self._intake.rows.get(doc_id)
        if row is None:
            raise KeyError(document_id)
        owner, document = row
        self._intake.rows[doc_id] = (owner, document.failed(reason))

    def seed_pieces(self, document_id: str, pieces: tuple[str, ...], extracted: str) -> None:
        doc_id = UUID(document_id)
        self._pieces_index.stored[doc_id] = pieces
        self._pieces_index.extracted_text[doc_id] = extracted
        self.replace_pieces(document_id, pieces, extracted)

    def bind_second_index_run(self, runner) -> None:
        self._second_index_run = runner

    def bind_dual_claim_race(self, runner) -> None:
        self._dual_claim_race_run = runner

    def trigger_second_indexing_run(self, document_id: str) -> None:
        if self._second_index_run is None:
            raise RuntimeError("second indexing run hook is not bound")
        self._second_index_run(document_id)

    def piece_replace_count(self, document_id: str) -> int:
        return self._piece_write_counts.get(document_id, 0)

    def block_pdf_read(self) -> None:
        self._pdf_read_allowed.clear()

    def allow_pdf_read(self) -> None:
        self._pdf_read_allowed.set()

    def pdf_read_allowed(self) -> bool:
        return self._pdf_read_allowed.is_set()

    def trigger_dual_claim_race(self) -> None:
        if self._dual_claim_race_run is None:
            raise RuntimeError("dual claim race hook is not bound")
        self._dual_claim_race_run()

    def arm_dual_claim_sync(self) -> None:
        self._dual_claim_sync = True
        self._dual_claim_barrier = asyncio.Event()
        self._dual_claim_arrivals = 0

    def disarm_dual_claim_sync(self) -> None:
        self._dual_claim_sync = False
        self._dual_claim_barrier = None
        self._dual_claim_arrivals = 0

    async def synchronize_dual_claim(self, document_id: str) -> None:
        if not self._dual_claim_sync or self._dual_claim_barrier is None:
            return
        self._dual_claim_arrivals += 1
        if self._dual_claim_arrivals >= 2:
            self._dual_claim_barrier.set()
        await self._dual_claim_barrier.wait()

    def replace_count(self, document_id: str) -> int:
        return self._replace_counts.get(document_id, 0)

    def mark_indexing_always_fails(self, document_id: str) -> None:
        self._indexing_always_fails.add(document_id)

    def indexing_always_fails(self, document_id: str) -> bool:
        return document_id in self._indexing_always_fails

    def arm_search_store_fails_once_for_all(self) -> None:
        self._search_store_fail_once_armed = True
        self._search_store_fail_once_consumed = False

    def search_store_should_fail_once(self) -> bool:
        return self._search_store_fail_once_armed and not self._search_store_fail_once_consumed

    def consume_search_store_fail_once(self) -> None:
        self._search_store_fail_once_consumed = True

    def record_indexing_attempt(self, document_id: str) -> None:
        self._indexing_attempts[document_id] = self._indexing_attempts.get(document_id, 0) + 1
        self._indexing_attempt_times.setdefault(document_id, []).append(time.monotonic())

    def indexing_attempts(self, document_id: str) -> int:
        return self._indexing_attempts.get(document_id, 0)

    def document_owner(self, document_id: str) -> str:
        doc_id = UUID(document_id)
        row = self._intake.rows.get(doc_id)
        if row is None:
            raise KeyError(document_id)
        return str(row[0])

    def indexing_attempt_times(self, document_id: str) -> tuple[float, ...]:
        return tuple(self._indexing_attempt_times.get(document_id, ()))

    def set_search_store_outcome(self, outcome: str) -> None:
        self._search_store_outcome = outcome

    def search_store_outcome(self) -> str | None:
        return self._search_store_outcome

    def search_store_timeout_seconds(self) -> float:
        return self._search_store_timeout_seconds

    def prepare_virus_and_search_store_calls(self) -> None:
        self._virus_call_delay = None
        self._search_store_call_delay = None
        self.set_virus_outcome("clears")
        self.set_search_store_outcome(None)

    def set_virus_call_finishes_just_before_its_deadline(self) -> None:
        self._virus_call_delay = self._external_call_deadline_seconds - 0.02
        self.set_virus_outcome("clears")

    def set_virus_call_reaches_its_deadline(self) -> None:
        self._virus_call_delay = self._external_call_deadline_seconds + 0.02
        self.set_virus_outcome("clears")

    def set_search_store_call_finishes_just_before_its_deadline(self) -> None:
        self._search_store_call_delay = self._external_call_deadline_seconds - 0.02
        self.set_search_store_outcome(None)

    def set_search_store_call_reaches_its_deadline(self) -> None:
        self._search_store_call_delay = self._external_call_deadline_seconds + 0.02
        self.set_search_store_outcome("times out")

    def virus_call_delay_seconds(self) -> float:
        return 0.0 if self._virus_call_delay is None else self._virus_call_delay

    def search_store_call_delay_seconds(self) -> float:
        return 0.0 if self._search_store_call_delay is None else self._search_store_call_delay

    def external_call_deadline_seconds(self) -> float:
        return self._external_call_deadline_seconds

    def set_embedding_outcome(self, outcome: str) -> None:
        self._embedding_outcome = outcome

    def embedding_outcome(self) -> str | None:
        return self._embedding_outcome

    def clear_embedding_outcome(self) -> None:
        self._embedding_outcome = None

    def record_embedding_attempt(self, document_id: str) -> None:
        self._embedding_attempts[document_id] = self._embedding_attempts.get(document_id, 0) + 1

    def embedding_attempts(self, document_id: str) -> int:
        return self._embedding_attempts.get(document_id, 0)
