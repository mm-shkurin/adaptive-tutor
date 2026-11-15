import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAVectorRunThatStopsMidway(AbstractBackendTest):
    """A vector run that stops midway does not store those pieces twice.

    Given a signed-in person
    And a ready PDF whose vector run stored some pieces and then failed
    When the person opens the chat again
    Then the pieces already stored are not stored again
    And the pieces after the failed one are still attempted
    And the run records which piece failed
    And the person-facing notice stays the fixed sentence
    And the chat stays not askable until the run finishes
    """

    def test_should_resume_without_duplicating_stored_pieces(self, chats):
        chats.given_a_signed_in_person()
        chats.and_a_ready_pdf_whose_vector_run_stored_some_pieces_and_then_failed()
        chats.when_the_person_opens_the_chat_again_after_a_partial_vector_run()
        chats.then_the_pieces_already_stored_are_not_stored_again()
        chats.then_the_pieces_after_the_failed_one_are_still_attempted()
        chats.then_the_run_records_which_piece_failed()
        chats.then_the_person_facing_notice_stays_the_fixed_sentence()
        chats.then_the_chat_stays_not_askable_until_the_run_finishes()
