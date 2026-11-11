import asyncio

from usecase.document.indexing_budget import DEADLINE_SECONDS
from usecase.tests.fake.document.fake_index_documents import FakeIndexDocuments
from usecase.tests.statements import document_views as views
from usecase.tests.statements.document_fixture_text import TABLE_NAMED


class IndexingDeadlineStatements:
    async def given_an_accepted_document_that_is_still_indexing(self) -> None:
        self._reader.block()
        self.upload = (
            await self._accept(self.person_id, self.scope.lecture_name, self.lecture)
        ).document
        self._indexing_task = asyncio.create_task(self.index.index_waiting())
        self.indexing_started_at = self.clock.now()
        for _ in range(40):
            current = await self.read.read(self.person_id, self.upload.id)
            if current.status == "indexing":
                self.indexing_started_at = self.clock.now()
                return
            await asyncio.sleep(0.05)
        raise AssertionError("document did not enter indexing")

    async def when_the_clock_is_just_short_of_five_minutes(self) -> None:
        elapsed = (self.clock.now() - self.indexing_started_at).total_seconds()
        remaining = DEADLINE_SECONDS - 1 - elapsed
        assert remaining > 0
        self.clock.advance(int(remaining))
        await asyncio.sleep(0.1)

    async def then_the_document_is_still_indexing(self) -> None:
        current = await self.read.read(self.person_id, self.upload.id)
        assert current.status == "indexing"

    async def when_five_minutes_have_passed(self) -> None:
        self.clock.advance(1)
        await asyncio.wait_for(self._indexing_task, timeout=2)
        self.finished = await self.read.read(self.person_id, self.upload.id)

    async def then_the_document_is_failed_after_five_minutes(self) -> None:
        assert self.finished == views.failed(
            self.upload.id,
            self.scope.lecture_name,
            len(self.lecture),
            "indexing timed out",
        )

    async def then_in_flight_indexing_is_cancelled(self) -> None:
        self._reader.allow()
        await asyncio.sleep(0.1)
        await self.index.index_waiting()
        self.finished = await self.read.read(self.person_id, self.upload.id)
        assert self.finished == views.failed(
            self.upload.id,
            self.scope.lecture_name,
            len(self.lecture),
            "indexing timed out",
        )

    async def then_nothing_is_stored_after_that_instant(self) -> None:
        assert self.upload.id not in self.pieces.stored
        assert await self.pieces.pieces(self.upload.id) == ()

    async def when_the_person_submits_a_pdf_that_is_costly_to_read_but_within_the_size_limit(
        self,
    ) -> None:
        await self.given_an_accepted_document_that_is_still_indexing()

    async def then_indexing_finishes_or_fails_within_five_minutes(self) -> None:
        self.clock.advance(DEADLINE_SECONDS)
        await asyncio.wait_for(self._indexing_task, timeout=2)
        self.finished = await self.read.read(self.person_id, self.upload.id)
        assert self.finished.status in {"ready", "failed"}

    async def then_it_does_not_keep_running_after_that(self) -> None:
        terminal_status = self.finished.status
        pieces_before = await self.pieces.pieces(self.upload.id)
        replace_before = self.pieces.replace_count(self.upload.id)
        self.clock.advance(60)
        self._reader.allow()
        await asyncio.sleep(0.1)
        await self.index.index_waiting()
        self.finished = await self.read.read(self.person_id, self.upload.id)
        assert self.finished.status == terminal_status
        assert await self.pieces.pieces(self.upload.id) == pieces_before
        assert self.pieces.replace_count(self.upload.id) == replace_before

    async def given_a_document_that_is_finished(self, finished: str) -> None:
        self.expected_finished_status = finished
        await self.given_a_signed_in_person()
        if finished == "ready":
            await self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
            await self.when_indexing_finishes()
            self.finished = self.ready
        else:
            await self.when_indexing_fails_on_one_table_after_an_earlier_step_succeeded()
            assert self.finished.status == "failed"

    async def when_indexing_is_requested_again_for_that_document(self) -> None:
        if isinstance(self.index, FakeIndexDocuments):
            self.index._fail_table_after_text = False
        self.pieces_before_second_index = await self.pieces.pieces(self.finished.id)
        self.reads_before_second_index = self._reader.read_count
        await self.index._index(self.finished, self.lecture)
        self.finished = await self.read.read(self.person_id, self.finished.id)

    async def then_the_document_stays_finished(self) -> None:
        assert self._reader.read_count == self.reads_before_second_index
        if self.expected_finished_status == "ready":
            assert self.finished == views.ready(
                self.finished.id, self.scope.lecture_name, len(self.lecture)
            )
        else:
            assert self.finished == views.failed(
                self.finished.id, self.scope.lecture_name, len(self.lecture), TABLE_NAMED
            )

    async def then_no_second_set_of_pieces_is_stored(self) -> None:
        assert await self.pieces.pieces(self.finished.id) == self.pieces_before_second_index
