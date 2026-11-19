import pytest

from statements.reply_statements import NOT_IN_MATERIAL
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestNothingInTheMaterialShowsEmptySources(AbstractUiTest):
    """UI Test Scenario 1.2: Nothing in the material shows an empty sources panel

    Given a signed-in person whose last reply is not in the material
    When the person opens that chat
    Then the tutor says it is not in the material
    And the sources panel is empty
    """

    def test_should_show_missing_reply_with_empty_sources(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_whose_last_reply_is_not_in_the_material()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.then_the_tutor_shows_text(NOT_IN_MATERIAL)
        chat_screen.then_the_sources_panel_is_empty()
