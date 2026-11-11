from usecase.tests.fake.document.fake_index_documents import FakeIndexDocuments
from usecase.tests.statements import document_views as views


class EmbeddingStatements:
    async def and_the_embedding_call(self, outcome: str) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        mapped = {
            "refuses": "refuses",
            "answers unreadable": "unreadable",
            "fails as a server error": "server_error",
        }
        self.index.set_embedding_outcome(mapped[outcome])
        self.embedding_outcome = outcome

    async def when_indexing_runs_for_embedding(self) -> None:
        await self.index.index_waiting()
        self.finished = await self.read.read(self.person_id, self.upload.id)

    async def then_the_document_is_failed_and_not_retried_for_that_refusal(self) -> None:
        assert self.finished == views.failed(
            self.upload.id,
            self.scope.lecture_name,
            len(self.lecture),
            "embedding refused",
        )
        attempts = self.index.embedding_attempts(self.upload.id)
        await self.index.index_waiting()
        later = await self.read.read(self.person_id, self.upload.id)
        assert later.status == "failed"
        assert self.index.embedding_attempts(self.upload.id) == attempts

    async def then_the_document_is_failed_after_unreadable_embedding(self) -> None:
        assert self.finished == views.failed(
            self.upload.id,
            self.scope.lecture_name,
            len(self.lecture),
            "embedding refused",
        )

    async def then_the_server_error_try_counts_toward_the_three(self) -> None:
        assert self.finished.status in {"waiting", "indexing"}
        assert self.index.embedding_attempts(self.upload.id) == 1
