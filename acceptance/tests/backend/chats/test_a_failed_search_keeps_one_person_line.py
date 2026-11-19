import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAFailedSearchKeepsOnePersonLine(AbstractBackendTest):
    """A failed search keeps one person line and no tutor line.

    Given a signed-in person with an askable chat
    And the search fails
    When the person sends a line
    Then the thread has one person line
    And the thread has no tutor line
    """

    @pytest.mark.parametrize(
        "how",
        [
            "times out",
            "returns a 4xx status",
            "returns a 5xx status",
            "returns a malformed body",
        ],
    )
    def test_should_keep_one_person_line(self, chats, how):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.and_the_search_fails(how)
        chats.when_the_person_sends_a_line_expecting_failure()
        chats.then_the_thread_has_one_person_line()
        chats.then_the_thread_has_no_tutor_line()
