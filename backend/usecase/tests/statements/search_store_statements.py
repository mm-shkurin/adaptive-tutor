from usecase.tests.statements import document_views as views


class SearchStoreStatements:
    async def and_the_search_store(self, outcome: str) -> None:
        self.pieces.set_outcome(outcome)

    async def when_indexing_runs(self) -> None:
        await self.index.index_waiting()
        self.finished = await self.read.read(self.person_id, self.upload.id)

    async def then_the_document_is_failed_after_search_store(self) -> None:
        assert self.finished == views.failed(
            self.upload.id,
            self.scope.lecture_name,
            len(self.lecture),
            "search store refused",
        )

    async def then_the_finished_document_is_not_ready(self) -> None:
        assert self.finished.status != "ready"

    async def then_the_failure_is_visible_on_the_document(self) -> None:
        assert self.finished.status == "failed"
        assert self.finished.error
        assert self.finished.error != ""
