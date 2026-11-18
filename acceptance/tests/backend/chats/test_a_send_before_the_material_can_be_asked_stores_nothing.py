import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestASendBeforeTheMaterialCanBeAskedStoresNothing(AbstractBackendTest):
    """A send before the material can be asked stores nothing.

    Given a signed-in person whose chat cannot be asked yet
    When the person sends a line
    Then the send is refused
    And the thread has no person line and no tutor line
    """

    def test_should_refuse_the_send_and_store_no_lines(self, chats):
        chats.given_a_signed_in_person_whose_chat_cannot_be_asked_yet()
        chats.when_the_person_sends_a_line_while_not_askable()
        chats.then_the_send_is_refused_as_not_askable()
        chats.then_the_thread_has_no_person_line_and_no_tutor_line()
