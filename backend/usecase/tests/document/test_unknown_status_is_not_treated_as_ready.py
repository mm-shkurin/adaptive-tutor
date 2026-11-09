from dataclasses import replace
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parents[4] / "acceptance" / "fixtures"
FIVE_HUNDRED = (FIXTURES / "five_hundred.txt").read_text(encoding="utf-8")
EXTRACTED = (FIXTURES / "extracted.txt").read_text(encoding="utf-8")
UNKNOWN_STATUS = "corrupted"


class TestUnknownStatusIsNotTreatedAsReady:
    """An unknown status is not treated as ready.

    Given an accepted document
    When the document is given a status that is not waiting, indexing, ready, or failed
    Then the document is not ready
    And nothing from the file is newly searchable
    """

    @pytest.mark.asyncio
    async def test_should_not_treat_an_unknown_status_as_ready(self, documents):
        await documents.given_a_signed_in_person()
        await documents.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        await documents.then_the_upload_is_answered_before_indexing_finishes()
        await documents.pieces.replace(documents.upload.id, (FIVE_HUNDRED,), EXTRACTED)
        owner, document = documents.index.intake.rows[documents.upload.id]
        documents.index.intake.rows[documents.upload.id] = (
            owner,
            replace(document, status=UNKNOWN_STATUS),
        )
        read_back = await documents.read.read(documents.person_id, documents.upload.id)
        assert read_back.status == UNKNOWN_STATUS
        assert not read_back.is_ready()
        assert await documents.search.pieces_for(documents.person_id, documents.upload.id) == ()
        assert await documents.search.extracted_text(documents.person_id, documents.upload.id) == ""
