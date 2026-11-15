import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestOpeningAPdfThatAlreadyHasVectors(AbstractBackendTest):
    """Opening a PDF that already has vectors does not write them again.

    Given a signed-in person
    And a ready PDF that already has vectors
    When the person opens a chat on that PDF twice
    Then the vectors are not written again
    """

    def test_should_not_write_vectors_again(self, chats):
        chats.given_a_signed_in_person()
        chats.and_a_ready_pdf_that_already_has_vectors()
        chats.when_the_person_opens_a_chat_on_that_pdf_twice()
        chats.then_the_vectors_are_not_written_again()
