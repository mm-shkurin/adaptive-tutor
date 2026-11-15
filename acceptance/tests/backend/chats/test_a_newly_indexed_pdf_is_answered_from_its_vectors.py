import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestANewlyIndexedPdfIsAnsweredFromItsVectors(AbstractBackendTest):
    """A newly indexed PDF is answered from its vectors and the stored starting page.

    Given a signed-in person
    And a new PDF that finishes indexing
    When the person asks a question that the PDF contains
    Then the vectors are 384-dimensional
    And the reply uses only pieces of this PDF
    And the page is the starting page stored while the file was in hand
    """

    def test_should_answer_from_the_stored_vectors_and_starting_page(self, chats):
        chats.given_a_signed_in_person()
        chats.and_a_new_pdf_that_finishes_indexing()
        chats.when_the_person_asks_a_question_that_the_pdf_contains()
        chats.then_the_vectors_are_384_dimensional()
        chats.then_the_reply_uses_only_pieces_of_this_pdf()
        chats.then_the_page_is_the_starting_page_stored_while_the_file_was_in_hand()
