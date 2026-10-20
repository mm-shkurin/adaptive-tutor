import pytest


class TestAcceptedPdfBecomesReady:
    """An accepted PDF becomes ready and its text and tables can be searched.

    Given a signed-in person
    And a neighbour with indexed text
    When the person submits a valid PDF that contains text and a table
    Then the upload is answered before indexing finishes
    And the next read shows the document as waiting, not a stale copy
    And the document then becomes ready
    And the ready document shows the file name, the byte size, the page count, and the piece count
    And the ready document has no failure reason
    And the person's search finds the text and the table
    And the extracted text matches the PDF byte for byte after canonical composition
    And the neighbour's text is absent
    And a piece of 500 tokens is kept
    And a shorter piece is joined onward
    And the original file is gone
    And the neighbour's file is still there
    """

    @pytest.mark.skip(reason="RED: SubmitDocument.submit raises NotImplementedError")
    @pytest.mark.asyncio
    async def test_should_become_ready_and_search_the_text_and_the_table(self, documents):
        await documents.given_a_signed_in_person()
        await documents.given_a_neighbour_account()
        await documents.when_the_neighbour_submits_a_pdf()
        await documents.then_the_neighbour_upload_is_waiting()
        await documents.when_the_neighbour_document_is_indexed()
        await documents.then_the_neighbour_document_is_ready()
        await documents.when_the_neighbour_text_is_searched()
        await documents.then_the_neighbour_text_is_indexed()
        await documents.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        await documents.then_the_upload_is_answered_before_indexing_finishes()
        await documents.when_the_person_reads_the_upload()
        await documents.then_the_next_read_shows_the_document_as_waiting_not_a_stale_copy()
        await documents.when_indexing_finishes()
        await documents.then_the_document_becomes_ready()
        await documents.then_the_ready_document_shows_the_file_name_size_pages_and_pieces()
        await documents.then_the_ready_document_has_no_failure_reason()
        await documents.when_the_person_searches_the_lecture()
        await documents.then_the_persons_search_finds_the_text_and_the_table()
        await documents.when_the_extracted_text_is_read()
        await documents.then_the_extracted_text_matches_after_canonical_composition()
        await documents.when_the_neighbours_text_absence_is_checked()
        await documents.then_the_neighbours_text_is_absent()
        await documents.when_the_person_searches_the_lecture()
        await documents.then_a_piece_of_500_tokens_is_kept()
        await documents.when_the_person_searches_the_lecture()
        await documents.then_a_shorter_piece_is_joined_onward()
        await documents.when_the_original_file_is_read()
        await documents.then_the_original_file_is_gone()
        await documents.when_the_neighbours_file_is_read()
        await documents.then_the_neighbours_file_is_still_there()
