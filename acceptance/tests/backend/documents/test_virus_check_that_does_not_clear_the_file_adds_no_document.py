import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestVirusCheckThatDoesNotClearTheFileAddsNoDocument(AbstractBackendTest):
    """A virus check that does not clear the file adds no document.

    Scenario Outline:
    Given a signed-in person with one document
    And the virus check <outcome>
    When the person submits a PDF
    Then the upload is refused
    And the list is unchanged
    And the file is not indexed
    """

    @pytest.mark.parametrize(
        "outcome",
        [
            "finds a virus",
            "times out",
            "answers unreadable",
        ],
    )
    def test_should_refuse_the_upload_and_leave_the_list_unchanged(self, documents, outcome):
        """Given a signed-in person with one document
        And the virus check does not clear the file
        When the person submits a PDF
        Then the upload is refused
        And the list is unchanged
        And the file is not indexed
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.given_the_virus_check(outcome)
        documents.when_the_person_submits_a_pdf()
        documents.then_the_upload_is_refused("virus_detected")
        documents.then_the_list_is_unchanged()
        documents.then_the_file_is_not_indexed()
