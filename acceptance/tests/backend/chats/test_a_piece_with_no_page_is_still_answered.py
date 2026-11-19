import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAPieceWithNoPageIsStillAnswered(AbstractBackendTest):
    """A piece with no page is still answered and the source has no page.

    Given a signed-in person with an askable chat
    And the retrieved piece has no page
    When the person sends a question
    Then the tutor answers
    And the bubble has no page
    And the source shows the piece text without a page
    """

    def test_should_answer_from_a_piece_without_a_page(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.and_the_retrieved_piece_has_no_page()
        chats.when_the_person_sends_a_question()
        chats.then_the_tutor_answers()
        chats.then_the_bubble_has_no_page()
        chats.then_the_source_shows_the_piece_text_without_a_page()
