import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAMissingModelKeyFailsTheSend(AbstractBackendTest):
    """A missing model key fails the send.

    Given the app is running with the model key unset
    And a signed-in person with an askable chat
    When the person sends a line
    Then the reply fails
    And the thread has one person line and no tutor line
    And the failure shows no secret, no stack, and no file path
    """

    def test_should_fail_the_reply_without_leaking(self, chats):
        chats.given_the_app_is_running_with_the_model_key_unset()
        chats.when_the_person_sends_a_line_with_no_model_key()
        chats.then_the_reply_fails_without_secret_stack_or_path()
