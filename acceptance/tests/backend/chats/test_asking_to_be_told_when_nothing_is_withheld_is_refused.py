import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAskingToBeToldWhenNothingIsWithheldIsRefused(AbstractBackendTest):
    """Asking to be told when nothing is withheld is refused.

    Given a signed-in person with an askable chat that is not withholding
    When the person asks to be told
    Then the send is refused
    And the thread is unchanged
    """

    def test_should_refuse_tell_when_nothing_is_withheld(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat_that_is_not_withholding()
        chats.when_the_person_asks_to_be_told()
        chats.then_the_tell_is_refused()
        chats.then_the_thread_is_unchanged_after_tell_refusal()
