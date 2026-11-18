import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAScriptAndASqlFragmentRoundTrip(AbstractBackendTest):
    """A script and a SQL fragment round-trip as the person's own text.

    Given a signed-in person with an askable chat
    And a retrieved piece whose text contains a script and a SQL fragment
    When the person sends a line that contains a script and a SQL fragment
    Then the thread shows that line unchanged
    And the source shows that piece unchanged
    And the chat list still contains only this person's chats
    """

    def test_should_round_trip_hostile_text_unchanged(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.and_a_retrieved_piece_whose_text_contains_a_script_and_a_sql_fragment()
        chats.when_the_person_sends_a_line_that_contains_a_script_and_a_sql_fragment()
        chats.then_the_thread_shows_that_hostile_line_unchanged()
        chats.then_the_chat_list_still_contains_only_this_persons_chats()
