import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestANewAttemptAfterAFailedReplyIsKept(AbstractBackendTest):
    """A new attempt after a failed reply is kept.

    Given a signed-in person whose last reply failed
    When the person sends a new attempt
    Then that person line is kept
    """

    def test_should_keep_the_new_person_line(self, chats):
        chats.given_a_signed_in_person_whose_last_reply_failed()
        chats.when_the_person_sends_a_new_attempt()
        chats.then_that_person_line_is_kept()
