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
