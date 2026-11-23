import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestScriptInTopicQuestionChoiceShownAsText(AbstractUiTest):
    """UI 1.5: A script in the topic, the question, and a choice is shown as text."""

    def test_should_render_script_mark_as_text(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_a_script_marked_quiz()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_the_card()
        quiz_screen.then_script_mark_is_shown_as_text(quiz_browser.script_mark)
