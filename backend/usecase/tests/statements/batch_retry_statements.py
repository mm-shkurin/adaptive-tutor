import asyncio

from usecase.tests.fake.document.fake_index_documents import FakeIndexDocuments

BATCH_RETRY_DOCUMENT_COUNT = 5


class BatchRetryStatements:
    async def given_many_accepted_documents(self) -> None:
        await self.given_a_signed_in_person()
        self.batch_document_ids = []
        for index in range(BATCH_RETRY_DOCUMENT_COUNT):
            accepted = await self._accept(
                self.person_id, f"batch-retry-{index}.pdf", self.neighbour_pdf
            )
            self.batch_document_ids.append(accepted.document.id)

    async def and_the_search_store_fails_once_for_all_of_them(self) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        self.index.arm_search_store_fails_once_for_all()


    async def when_they_retry(self) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        for _ in range(40):
            await self.index.index_waiting()
            await asyncio.sleep(0.01)
            if all(
                self.index.indexing_attempts(document_id) >= 2
                for document_id in self.batch_document_ids
            ):
                break

    async def then_the_retries_are_not_all_issued_at_the_same_instant(self) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        retry_starts: list[float] = []
        for document_id in self.batch_document_ids:
            attempts = self.index.indexing_attempt_times(document_id)
            assert len(attempts) >= 2, (
                f"document {document_id} expected a retry, got {len(attempts)} attempts"
            )
            retry_starts.append(attempts[1])
        spread = max(retry_starts) - min(retry_starts)
        assert spread > 0.0, "all retries were issued at the same instant"

    async def then_none_of_them_is_tried_more_than_three_times(self) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        for document_id in self.batch_document_ids:
            assert self.index.indexing_attempts(document_id) <= 3
