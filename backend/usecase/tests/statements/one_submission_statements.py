import asyncio
from uuid import uuid4

from usecase.document.errors import RateLimited
from usecase.document.submit_document import AcceptedSubmission


class OneSubmissionStatements:
    async def when_the_same_submission_is_delivered_twice(self) -> None:
        self.submission_key = str(uuid4())
        first = await self._accept(
            self.person_id, self.scope.lecture_name, self.lecture, self.submission_key
        )
        self.upload = first.document
        self.replay = await self._accept(
            self.person_id, self.scope.lecture_name, self.lecture, self.submission_key
        )

    async def then_one_document_exists_for_that_submission(self) -> None:
        documents, has_next = await self.listed.list(self.person_id, 1)
        assert len(documents) == 1
        assert has_next is False
        assert documents[0].id == self.upload.id

    async def then_the_second_delivery_does_not_add_a_second_document(self) -> None:
        assert self.replay.created is False
        assert self.replay.document.id == self.upload.id

    async def then_the_second_delivery_does_not_count_as_another_upload(self) -> None:
        for index in range(4):
            await self._accept(self.person_id, f"extra-{index}.pdf", self.lecture)
        try:
            await self._accept(self.person_id, "sixth.pdf", self.lecture)
            self.refusal = None
        except RateLimited as error:
            self.refusal = error
        assert isinstance(self.refusal, RateLimited)
        documents, _ = await self.listed.list(self.person_id, 1)
        assert len(documents) == 5

    async def when_two_overlapping_copies_of_one_submission_complete(self) -> None:
        self.submission_key = str(uuid4())
        self.race_results = await asyncio.gather(
            self._accept(
                self.person_id, self.scope.lecture_name, self.lecture, self.submission_key
            ),
            self._accept(
                self.person_id, self.scope.lecture_name, self.lecture, self.submission_key
            ),
        )
        self.upload = self.race_results[0].document

    async def then_one_document_exists_after_overlapping_copies(self) -> None:
        assert all(isinstance(item, AcceptedSubmission) for item in self.race_results)
        ids = {item.document.id for item in self.race_results}
        assert len(ids) == 1
        created = [item for item in self.race_results if item.created]
        assert len(created) == 1
        documents, has_next = await self.listed.list(self.person_id, 1)
        assert len(documents) == 1
        assert has_next is False
        assert documents[0].id == next(iter(ids))

    async def given_the_person_already_uploaded_a_pdf(self) -> None:
        self.earlier = (
            await self._accept(self.person_id, self.scope.lecture_name, self.lecture)
        ).document

    async def when_the_person_uploads_that_pdf_again_as_a_new_submission(self) -> None:
        self.second_upload = (
            await self._accept(self.person_id, self.scope.lecture_name, self.lecture)
        ).document

    async def then_two_documents_exist(self) -> None:
        documents, has_next = await self.listed.list(self.person_id, 1)
        assert len(documents) == 2
        assert has_next is False
        ids = {documents[0].id, documents[1].id}
        assert ids == {self.earlier.id, self.second_upload.id}

    async def then_the_earlier_document_is_unchanged(self) -> None:
        read_back = await self.read.read(self.person_id, self.earlier.id)
        assert read_back == self.earlier
