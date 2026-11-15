import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest

FAILURES = (
    "times out",
    "returns a 4xx status",
    "returns a 5xx status",
    "returns a malformed body",
)


@pytest.mark.backend
class TestAVectorRunThatFailsLeavesTheDocumentReady(AbstractBackendTest):
    """A vector run that fails leaves the document ready and the next open can finish.

    Given a signed-in person
    And a ready PDF with no vectors
    And the embedding call <fails>
    When the person opens a chat on that PDF
    Then the chat says the material cannot be asked yet
    And the library row stays ready
    When the embedding call succeeds and the person opens the chat again
    Then the chat becomes askable
    And pieces already stored are not stored again
    """

    @pytest.mark.parametrize("fails", FAILURES)
    def test_should_leave_ready_then_finish_on_the_next_open(self, chats, fails):
        chats.given_a_signed_in_person()
        chats.and_a_ready_pdf_with_no_vectors()
        chats.and_the_embedding_call(fails)
        chats.when_the_person_opens_a_chat_on_that_pdf()
        chats.then_the_chat_says_the_material_cannot_be_asked_yet()
        chats.then_the_library_row_stays_ready()
        chats.when_the_embedding_call_succeeds_and_the_person_opens_the_chat_again()
        chats.then_the_chat_becomes_askable()
        chats.then_pieces_already_stored_are_not_stored_again()
