import pytest

from statements.chat_screen_statements import EXAMINER_QUESTION, RELEASE
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestADoubleClickedControlStoresOneEffect(AbstractUiTest):
    """UI Test Scenario 3.14: A double-clicked Examiner, choice, or tell stores one effect

    Given a signed-in person who can <act>
    When the person activates that control twice without waiting
    Then one effect is stored
    """

    def test_should_store_one_examiner_question(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        signed_in_browser.script_tutor(EXAMINER_QUESTION)
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_activates_examiner_twice_without_waiting()
        signed_in_browser.then_one_examiner_question_is_stored()

    def test_should_store_one_choice_grade(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_with_an_open_examiner_question()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_activates_a_choice_twice_without_waiting("c1")
        signed_in_browser.then_one_grade_effect_is_stored()

    def test_should_store_one_tell_release(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_whose_tutor_is_withholding()
        signed_in_browser.script_tutor(RELEASE)
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_activates_tell_twice_without_waiting()
        signed_in_browser.then_one_tell_release_is_stored()
