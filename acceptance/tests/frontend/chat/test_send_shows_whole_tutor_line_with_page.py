import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestSendShowsWholeTutorLineWithPage(AbstractUiTest):
    """UI Test Scenario 3.1: Send shows the whole tutor line with the page

    Given a signed-in person with an askable chat
    When the person sends a question
    Then the tutor line appears whole
    And the line shows the model and the page
    """

    def test_should_show_whole_tutor_line_with_model_and_page(self, signed_in_browser, chat_screen):
        """UI Test Scenario 3.1: Send shows the whole tutor line with the page

        Given a signed-in person with an askable chat
        When the person sends a question
        Then the tutor line appears whole
        And the line shows the model and the page
        """
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_a_question()
        chat_screen.then_the_tutor_line_appears_whole_with_the_model_and_the_page(
            signed_in_browser.tutor_line,
            "auto",
            signed_in_browser.page,
        )
