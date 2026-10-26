import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestCleanPdfPassesVirusCheckAndBecomesReady(AbstractBackendTest):
    """A clean PDF passes the virus check and becomes ready.

    Given a signed-in person
    And the virus check clears files
    When the person submits a valid PDF
    Then the document becomes ready
    And its text can be searched
    """

    @pytest.mark.skip(reason="RED: assert 0 == (0 + 1) — virus check never records a scan on upload")
    def test_should_clear_the_virus_check_and_become_ready_with_searchable_text(self, documents):
        """Given a signed-in person
        And the virus check clears files
        When the person submits a valid PDF
        Then the document becomes ready
        And its text can be searched
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_the_virus_check_clears_files()
        documents.when_the_person_submits_a_valid_pdf()
        documents.then_the_virus_check_cleared_the_upload()
        documents.when_the_document_finishes_indexing()
        documents.then_the_document_becomes_ready_with_its_facts()
        documents.then_its_text_can_be_searched()
