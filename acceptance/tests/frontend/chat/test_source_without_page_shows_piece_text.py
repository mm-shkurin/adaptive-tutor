import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest

PAGELESS = "page-less-piece"
TUTOR = "Answer from a page-less piece."


@pytest.mark.frontend
class TestSourceWithoutPageShowsPieceText(AbstractUiTest):
    """UI Test Scenario 1.3: A source without a page shows the piece text and no page number

    Given a signed-in person whose reply cites a piece with no page
    When the person opens that chat
    Then the bubble has no page
    And the source shows the piece text without a page number
    """

    def test_should_show_source_text_without_page(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_whose_reply_cites_a_piece_with_no_page(
            PAGELESS, TUTOR
        )
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.then_the_tutor_bubble_has_no_page(TUTOR)
        chat_screen.then_the_source_shows_piece_text_without_a_page(PAGELESS)
