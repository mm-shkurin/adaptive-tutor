import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAVectorWriteWithNoDocument(AbstractBackendTest):
    """A vector write with no document leaves every neighbour untouched.

    Given a signed-in person
    And a neighbour who owns a ready PDF with vectors
    When a vector write is attempted with no document
    Then no piece and no vector is written
    And the neighbour's vectors are unchanged
    """

    def test_should_leave_neighbour_vectors_untouched(self, chats):
        chats.and_a_neighbour_who_owns_a_ready_pdf_with_vectors()
        chats.when_a_vector_write_is_attempted_with_no_document()
        chats.then_no_piece_and_no_vector_is_written()
        chats.then_the_neighbours_vectors_are_unchanged()
