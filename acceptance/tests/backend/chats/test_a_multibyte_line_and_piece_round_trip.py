import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAMultibyteLineAndPieceRoundTrip(AbstractBackendTest):
    """A multibyte line and a multibyte piece round-trip unchanged.

    Given a signed-in person with an askable chat
    And a retrieved piece whose text contains a multibyte character
    When the person sends a line that contains a multibyte character
    Then the thread shows that line unchanged
    And the source shows that piece unchanged
    """

    def test_should_round_trip_multibyte_line_and_piece(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.and_a_retrieved_piece_whose_text_contains_a_multibyte_character()
        chats.when_the_person_sends_a_line_that_contains_a_multibyte_character()
        chats.then_the_thread_shows_that_multibyte_line_unchanged()
        chats.then_the_source_shows_that_multibyte_piece_unchanged()
