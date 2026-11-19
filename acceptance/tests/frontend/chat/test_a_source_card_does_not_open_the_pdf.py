import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestASourceCardDoesNotOpenThePdf(AbstractUiTest):
    """UI Test Scenario 4.1: A source card does not open the PDF

    Given a signed-in person whose chat has a source
    When the person activates that source
    Then the PDF does not open
    And the source still shows the page and the piece text
    """

    def test_should_keep_the_source_without_opening_the_pdf(
        self, signed_in_browser, chat_screen
    ):
        """Given a signed-in person whose chat has a source
        When the person activates that source
        Then the PDF does not open
        And the source still shows the page and the piece text
        """
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_a_question()
        chat_screen.then_the_sources_show_the_page_and_the_piece_text(
            signed_in_browser.page, signed_in_browser.source_text
        )
        chat_screen.when_the_person_activates_that_source()
        chat_screen.then_the_pdf_does_not_open_and_the_source_still_shows(
            signed_in_browser.page, signed_in_browser.source_text
        )
