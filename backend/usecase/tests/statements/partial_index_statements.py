from usecase.tests.fake.document.fake_index_documents import FakeIndexDocuments
from usecase.tests.statements import document_views as views


class PartialIndexStatements:
    async def given_indexing_wrote_the_pieces_and_then_failed_before_recording_ready(self) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        self.index.fail_ready_save_after_pieces_once()
        await self.given_a_signed_in_person()
        self.upload = (
            await self._accept(self.person_id, self.scope.lecture_name, self.lecture)
        ).document
        await self.index.index_waiting()
        self.partial = await self.read.read(self.person_id, self.upload.id)
        assert self.partial.status == "indexing"
        assert self.pieces.replace_count(self.upload.id) == 1
        assert await self.pieces.pieces(self.upload.id) != ()
        self.virus_scans_before_retry = self.virus.scans
        self.piece_writes_before_retry = self.pieces.replace_count(self.upload.id)

    async def when_indexing_runs_again_after_partial(self) -> None:
        current = await self.read.read(self.person_id, self.upload.id)
        await self.index._index(current, self.lecture)
        self.ready = await self.read.read(self.person_id, self.upload.id)

    async def then_a_retry_does_not_run_the_virus_check_again(self) -> None:
        assert self.virus.scans == self.virus_scans_before_retry

    async def then_the_document_becomes_ready_or_failed_and_does_not_stay_waiting(self) -> None:
        assert self.ready.status in {"ready", "failed"}
        assert self.ready.status != "waiting"

    async def then_it_is_not_ready_while_the_pieces_are_incomplete(self) -> None:
        assert self.partial.status != "ready"
        assert self.partial.piece_count is None
        assert await self.pieces.pieces(self.upload.id) != ()

    async def then_a_retry_does_not_rewrite_pieces(self) -> None:
        assert self.pieces.replace_count(self.upload.id) == self.piece_writes_before_retry
        assert self.ready == views.ready(
            self.upload.id, self.scope.lecture_name, len(self.lecture)
        )
