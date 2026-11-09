from usecase.document.errors import InvalidDocument


class VirusCheckStatements:
    async def given_the_virus_check_clears_files(self) -> None:
        self.virus.clear_files()
        self.virus_scans_at_start = self.virus.scans

    async def when_the_person_submits_a_valid_pdf(self) -> None:
        self.upload = (
            await self._accept(self.person_id, self.scope.lecture_name, self.lecture)
        ).document

    async def then_the_virus_check_cleared_the_upload(self) -> None:
        assert self.virus.scans == self.virus_scans_at_start + 1

    async def when_the_document_finishes_indexing(self) -> None:
        await self.when_indexing_finishes()

    async def then_the_document_becomes_ready_with_its_facts(self) -> None:
        await self.then_the_document_becomes_ready()

    async def then_its_text_can_be_searched(self) -> None:
        await self.when_the_person_searches_the_lecture()
        await self.then_the_persons_search_finds_the_text_and_the_table()

    async def given_a_signed_in_person_with_one_document(self) -> None:
        await self.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        self.baseline_ids = {self.upload.id}

    async def given_the_virus_check(self, outcome: str) -> None:
        mapped = {
            "finds a virus": "finds_virus",
            "times out": "times_out",
            "answers unreadable": "answers_unreadable",
        }
        self.virus.set_outcome(mapped[outcome])

    async def when_the_person_submits_a_pdf(self) -> None:
        self.piece_ids_before_submit = set(self.pieces.stored)
        try:
            await self._accept(self.person_id, "second.pdf", self.neighbour_pdf)
            self.refusal = None
        except Exception as error:
            self.refusal = error

    async def then_the_upload_is_refused_virus(self) -> None:
        assert isinstance(self.refusal, InvalidDocument)
        assert self.refusal.code == "virus_detected"

    async def then_the_list_is_unchanged_after_virus_refusal(self) -> None:
        page, _ = await self.listed.list(self.person_id, 1)
        assert {document.id for document in page} == self.baseline_ids

    async def then_the_file_is_not_indexed_after_virus_refusal(self) -> None:
        assert set(self.pieces.stored) == self.piece_ids_before_submit
