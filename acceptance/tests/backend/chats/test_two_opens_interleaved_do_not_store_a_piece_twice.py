import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTwoOpensInterleavedDoNotStoreAPieceTwice(AbstractBackendTest):
    """Two opens interleaved do not store a piece twice.

    Given a signed-in person
    And a ready PDF that is being vectorized
    When two opens interleave between the read of which pieces have vectors and the write
    Then each piece has one vector
    """

    def test_should_keep_one_vector_per_piece(self, chats):
        chats.given_a_signed_in_person()
        chats.and_a_ready_pdf_that_is_being_vectorized()
        chats.when_two_opens_interleave_between_the_read_of_which_pieces_have_vectors_and_the_write()
        chats.then_each_piece_has_one_vector()
