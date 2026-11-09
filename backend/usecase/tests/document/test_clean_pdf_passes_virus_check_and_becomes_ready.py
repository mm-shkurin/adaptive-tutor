import pytest


class TestCleanPdfPassesVirusCheckAndBecomesReady:
    """A clean PDF passes the virus check and becomes ready.

    Given a signed-in person
    And the virus check clears files
    When the person submits a valid PDF
    Then the document becomes ready
    And its text can be searched
    """

    @pytest.mark.asyncio
    async def test_should_clear_the_virus_check_and_become_ready_with_searchable_text(
        self, documents
    ):
        await documents.given_a_signed_in_person()
        await documents.given_the_virus_check_clears_files()
        await documents.when_the_person_submits_a_valid_pdf()
        await documents.then_the_virus_check_cleared_the_upload()
        await documents.when_the_document_finishes_indexing()
        await documents.then_the_document_becomes_ready_with_its_facts()
        await documents.then_its_text_can_be_searched()
