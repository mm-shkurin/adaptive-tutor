import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestHostileNameAndFailureReasonStayText(AbstractBackendTest):
    """A hostile name and a hostile failure reason stay text.

    Given a signed-in person and a neighbour
    When the person uploads a PDF whose name contains query metacharacters and markup
    And a failed document's reason contains the same
    Then the stored name equals the submitted name
    And the list shows that name as text
    And the failure reason is shown as text
    And the markup is not treated as a control
    And the query metacharacters are not treated as a command
    And the neighbour's documents are unchanged
    And a line break in the name stays inside that one field
    And query metacharacters in the PDF text are not a command
    """

    def test_should_keep_hostile_name_and_failure_reason_as_text(self, documents):
        """Given a signed-in person and a neighbour
        When the person uploads a PDF whose name contains query metacharacters and markup
        And a failed document's reason contains the same
        Then the stored name equals the submitted name
        And the list shows that name as text
        And the failure reason is shown as text
        And the markup is not treated as a control
        And the query metacharacters are not treated as a command
        And the neighbour's documents are unchanged
        And a line break in the name stays inside that one field
        And query metacharacters in the PDF text are not a command
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_neighbour_account()
        documents.then_the_neighbour_is_signed_in()
        documents.when_the_neighbour_submits_a_pdf()
        documents.then_the_neighbour_upload_is_waiting()
        documents.when_the_neighbour_document_becomes_ready()
        documents.then_the_neighbour_document_is_ready()
        documents.when_the_person_uploads_a_pdf_whose_name_contains_query_metacharacters_and_markup()
        documents.when_a_failed_documents_reason_contains_the_same()
        documents.then_the_stored_name_equals_the_submitted_name()
        documents.when_the_person_lists_documents()
        documents.then_the_list_shows_that_name_as_text()
        documents.then_the_failure_reason_is_shown_as_text()
        documents.then_the_markup_is_not_treated_as_a_control()
        documents.then_the_query_metacharacters_are_not_treated_as_a_command()
        documents.then_the_neighbours_documents_are_unchanged()
        documents.when_the_person_reads_the_uploaded_document()
        documents.then_a_line_break_in_the_name_stays_inside_that_one_field()
        documents.then_query_metacharacters_in_the_pdf_text_are_not_a_command()
