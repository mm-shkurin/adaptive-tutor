import asyncio

from usecase.document.errors import RateLimited, RateUnavailable
from usecase.document.submit_document import AcceptedSubmission


class UploadRateStatements:
    async def given_five_accepted_uploads_in_the_current_minute(self) -> None:
        for index in range(5):
            await self._accept(self.person_id, f"lecture-{index}.pdf", self.lecture)

    async def given_four_accepted_uploads_in_the_current_minute(self) -> None:
        for index in range(4):
            await self._accept(self.person_id, f"lecture-{index}.pdf", self.lecture)

    async def when_the_person_submits_a_sixth_pdf(self) -> None:
        try:
            await self._accept(self.person_id, "sixth.pdf", self.lecture)
            self.refusal = None
        except RateLimited as error:
            self.refusal = error

    async def then_the_upload_is_refused_as_rate_limited(self) -> None:
        assert isinstance(self.refusal, RateLimited)
        assert self.refusal.code == "rate_limited"

    async def then_the_five_documents_stay(self) -> None:
        documents, has_next = await self.listed.list(self.person_id, 1)
        assert len(documents) == 5
        assert has_next is False

    async def when_two_uploads_pass_the_count_check_together(self) -> None:
        self.race_results = await asyncio.gather(
            self._accept(self.person_id, "race-a.pdf", self.lecture),
            self._accept(self.person_id, "race-b.pdf", self.lecture),
            return_exceptions=True,
        )

    async def then_one_of_them_is_accepted_and_the_other_is_refused(self) -> None:
        accepted = [item for item in self.race_results if isinstance(item, AcceptedSubmission)]
        refused = [item for item in self.race_results if isinstance(item, RateLimited)]
        assert len(accepted) == 1
        assert len(refused) == 1
        assert refused[0].code == "rate_limited"

    async def then_five_documents_exist(self) -> None:
        await self.then_the_five_documents_stay()

    async def when_the_clock_is_just_short_of_the_next_minute(self) -> None:
        seconds = 60 - self.clock.now().second - 1
        if seconds > 0:
            self.clock.advance(seconds)

    async def then_a_sixth_upload_is_still_refused(self) -> None:
        await self.when_the_person_submits_a_sixth_pdf()
        await self.then_the_upload_is_refused_as_rate_limited()

    async def when_the_minute_window_has_just_opened(self) -> None:
        self.clock.advance(2)

    async def then_the_next_upload_is_accepted(self) -> None:
        self.upload = (
            await self._accept(self.person_id, "next-minute.pdf", self.lecture)
        ).document
        assert self.upload.status == "waiting"

    async def then_the_five_from_the_previous_minute_stay(self) -> None:
        documents, has_next = await self.listed.list(self.person_id, 1)
        assert len(documents) == 6
        assert has_next is False

    async def given_the_upload_count_cannot_be_read(self) -> None:
        self.rates.fail_reads = True

    async def when_the_person_submits_a_valid_pdf_under_rate_check(self) -> None:
        try:
            await self._accept(self.person_id, self.scope.lecture_name, self.lecture)
            self.refusal = None
        except RateUnavailable as error:
            self.refusal = error

    async def then_the_upload_is_refused_as_rate_unavailable(self) -> None:
        assert isinstance(self.refusal, RateUnavailable)
        assert self.refusal.code == "rate_unavailable"

    async def then_no_document_is_added(self) -> None:
        documents, has_next = await self.listed.list(self.person_id, 1)
        assert documents == ()
        assert has_next is False
