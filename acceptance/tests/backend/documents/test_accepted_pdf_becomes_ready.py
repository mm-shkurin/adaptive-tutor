import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.skip(reason="RED: POST /api/v1/documents returns 404 (assert 404 == 201)")
@pytest.mark.backend
class TestAcceptedPdfBecomesReady(AbstractBackendTest):
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

    def test_should_answer_the_upload_before_indexing_finishes(self, documents):
        """Given a signed-in person
        When the person submits a valid PDF that contains text and a table
        Then the upload is answered before indexing finishes
        And the next read shows the document as waiting, not a stale copy
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        documents.then_the_upload_is_answered_before_indexing_finishes()
        documents.when_the_person_reads_the_upload()
        documents.when_the_person_lists_documents()
        documents.then_the_next_read_shows_waiting_not_a_stale_copy()

    def test_should_become_ready_with_name_size_pages_and_pieces(self, documents):
        """Given a signed-in person
        When the person submits a valid PDF that contains text and a table
        Then the document then becomes ready
        And the ready document shows the file name, the byte size, the page count, and the piece count
        And the ready document has no failure reason
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        documents.when_the_document_finishes_indexing()
        documents.then_the_document_becomes_ready_with_its_facts()

    def test_should_find_the_text_and_the_table_without_the_neighbours(self, documents):
        """Given a signed-in person
        And a neighbour with indexed text
        When the person submits a valid PDF that contains text and a table
        Then the person's search finds the text and the table
        And the extracted text matches the PDF byte for byte after canonical composition
        And the neighbour's text is absent
        And a piece of 500 tokens is kept
        And a shorter piece is joined onward
        And the original file is gone
        And the neighbour's file is still there
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_neighbour_account()
        documents.then_the_neighbour_is_signed_in()
        documents.when_the_neighbour_submits_a_pdf()
        documents.then_the_neighbour_upload_is_waiting()
        documents.when_the_neighbour_document_becomes_ready()
        documents.then_the_neighbour_document_is_ready()
        documents.then_the_neighbour_text_is_indexed()
        documents.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
        documents.when_the_document_finishes_indexing()
        documents.then_the_document_becomes_ready_with_its_facts()
        documents.then_the_persons_search_finds_the_text_and_the_table()
        documents.then_the_extracted_text_matches_the_pdf()
        documents.then_the_neighbours_text_is_absent()
        documents.then_a_piece_of_500_tokens_is_kept()
        documents.then_a_shorter_piece_is_joined_onward()
        documents.then_the_original_file_is_gone()
        documents.then_the_neighbours_file_is_still_there()
