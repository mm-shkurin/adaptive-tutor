import pytest


class TestHostileNameAndFailureReasonStayText:
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

    @pytest.mark.asyncio
    async def test_should_keep_hostile_name_and_failure_reason_as_text(self, documents):
        await documents.given_a_signed_in_person()
        await documents.given_a_neighbour_account()
        await documents.when_the_neighbour_submits_a_pdf()
        await documents.then_the_neighbour_upload_is_waiting()
        await documents.when_the_neighbour_document_is_indexed()
        await documents.then_the_neighbour_document_is_ready()
        await documents.when_the_neighbour_text_is_searched()
        await documents.then_the_neighbour_text_is_indexed()
        await documents.when_the_neighbours_file_is_read()
        await documents.then_the_neighbours_file_is_already_gone()
        await documents.when_the_person_uploads_a_pdf_whose_name_contains_query_metacharacters_and_markup()
        await documents.when_a_failed_documents_reason_contains_the_same()
        await documents.then_the_stored_name_equals_the_submitted_name()
        await documents.when_the_person_lists_documents()
        await documents.then_the_list_shows_that_name_as_text()
        await documents.then_the_failure_reason_is_shown_as_text()
        await documents.then_the_markup_is_not_treated_as_a_control()
        await documents.then_the_query_metacharacters_are_not_treated_as_a_command()
        await documents.then_the_neighbours_documents_are_unchanged()
        await documents.then_a_line_break_in_the_name_stays_inside_that_one_field()
        await documents.then_query_metacharacters_in_the_pdf_text_are_not_a_command()
