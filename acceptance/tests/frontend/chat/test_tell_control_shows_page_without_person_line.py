import pytest

from statements.chat_screen_statements import RELEASE, SOCRATIC_QUESTION
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestTellControlShowsPageWithoutPersonLine(AbstractUiTest):
    """UI Test Scenario 3.6: The tell control shows the page without a person line

    Given a signed-in person whose tutor is withholding
    When the person uses the tell control
    Then the answer with a page is shown
    And no person line is added
    """

    def test_should_release_answer_without_new_person_line(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_whose_tutor_is_withholding()
        signed_in_browser.script_tutor(RELEASE)
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_uses_the_tell_control()
        chat_screen.then_the_answer_with_a_page_is_shown_without_a_new_person_line(
            RELEASE,
            signed_in_browser.page,
        )
