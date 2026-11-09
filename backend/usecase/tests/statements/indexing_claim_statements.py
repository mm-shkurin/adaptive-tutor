import asyncio

from usecase.tests.statements import document_views as views


class IndexingClaimStatements:
    async def given_an_accepted_document(self) -> None:
        await self.given_a_signed_in_person()
        await self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        await self.then_the_upload_is_answered_before_indexing_finishes()

    async def when_two_indexing_claims_pass_the_status_check_together(self) -> None:
        intake = self.index.intake
        intake.arm_dual_claim()
        try:
            self.claims = await asyncio.gather(intake.next_waiting(), intake.next_waiting())
        finally:
            intake.disarm_dual_claim()
        claimed = [claim for claim in self.claims if claim is not None]
        if claimed:
            await self.index._index(claimed[0][0], claimed[0][1])
        self.ready = await self.read.read(self.person_id, self.upload.id)
        self.lecture_pieces = await self.search.pieces_for(self.person_id, self.upload.id)

    async def then_one_claim_proceeds(self) -> None:
        assert sum(1 for claim in self.claims if claim is not None) == 1
        assert self.pieces.replace_count(self.upload.id) == 1

    async def then_one_set_of_pieces_is_stored(self) -> None:
        assert self.ready == views.ready(self.upload.id, self.scope.lecture_name, len(self.lecture))
        await self._assert_lecture_pieces()

    async def given_indexing_of_a_document_is_still_running(self) -> None:
        await self.given_an_accepted_document_that_is_still_indexing()

    async def when_a_second_indexing_run_starts_for_that_document(self) -> None:
        current = await self.read.read(self.person_id, self.upload.id)
        self._second_index_task = asyncio.create_task(self.index._index(current, self.lecture))
        await asyncio.sleep(0.2)

    async def then_the_two_runs_do_not_both_write_pieces(self) -> None:
        self._reader.allow()
        await asyncio.wait_for(self._indexing_task, timeout=5)
        await asyncio.wait_for(self._second_index_task, timeout=5)
        assert self._reader.read_count == 1
        assert self.pieces.replace_count(self.upload.id) == 1

    async def then_one_set_of_pieces_exists(self) -> None:
        self.ready = await self.read.read(self.person_id, self.upload.id)
        assert self.ready == views.ready(self.upload.id, self.scope.lecture_name, len(self.lecture))
        self.lecture_pieces = await self.search.pieces_for(self.person_id, self.upload.id)
        await self._assert_lecture_pieces()

    async def given_a_document_loaded_twice_while_it_is_indexing(self) -> None:
        await self.given_an_accepted_document_that_is_still_indexing()
        current = await self.read.read(self.person_id, self.upload.id)
        assert current.status == "indexing"
        self._stale_loads = (current, current)

    async def when_one_save_marks_it_ready_and_the_other_marks_it_failed(self) -> None:
        from usecase.tests.statements.document_statements import EXTRACTED, FIVE_HUNDRED, JOINED

        ready_write = self._stale_loads[0].ready(views.PAGE_COUNT, views.PIECE_COUNT)
        failed_write = self._stale_loads[1].failed("forced")
        await self.pieces.replace(self.upload.id, (FIVE_HUNDRED, JOINED), EXTRACTED)
        await self.index.intake.save(ready_write)
        await self.index.intake.save(failed_write)
        self.finished = await self.read.read(self.person_id, self.upload.id)
        self.lecture_pieces = await self.search.pieces_for(self.person_id, self.upload.id)

    async def then_the_later_save_does_not_silently_discard_the_earlier_one(self) -> None:
        assert self.finished.status == "ready"

    async def then_the_document_ends_in_exactly_one_of_those_statuses(self) -> None:
        assert self.finished.status in {"ready", "failed"}

    async def then_the_pieces_match_that_status(self) -> None:
        if self.finished.status == "ready":
            assert self.finished == views.ready(
                self.upload.id, self.scope.lecture_name, len(self.lecture)
            )
            await self._assert_lecture_pieces()
        else:
            assert self.lecture_pieces == ()
            assert await self.pieces.pieces(self.upload.id) == ()
