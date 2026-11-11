from usecase.tests.statements import document_views as views


class CallDeadlineStatements:
    async def given_a_virus_check_and_a_search_store_call(self) -> None:
        self.virus.prepare_call()
        self.pieces.prepare_call()

    async def when_the_virus_check_finishes_just_before_its_deadline(self) -> None:
        self.virus.finish_just_before_deadline()

    async def when_the_virus_check_reaches_its_deadline(self) -> None:
        self.virus.reach_deadline()

    async def when_the_person_submits_a_pdf_for_virus_deadline_check(self) -> None:
        await self.when_the_person_submits_a_pdf()

    async def then_the_external_call_still_counts_as_answered_for_the_upload(self) -> None:
        assert self.upload == views.waiting(
            self.upload.id, self.scope.lecture_name, len(self.lecture)
        )

    async def when_the_search_store_call_finishes_just_before_its_deadline(self) -> None:
        self.pieces.prepare_call()
        self.pieces.finish_just_before_deadline()

    async def when_the_search_store_call_reaches_its_deadline(self) -> None:
        self.pieces.prepare_call()
        self.pieces.reach_deadline()

    async def then_the_external_call_still_counts_as_answered_for_indexing(self) -> None:
        assert self.finished == views.ready(
            self.upload.id, self.scope.lecture_name, len(self.lecture)
        )

    async def then_the_search_store_fails_the_document(self) -> None:
        await self.then_the_document_is_failed_after_search_store()
        await self.then_nothing_from_the_file_can_be_searched()
