import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestFailedGenerationShowsAssembleError(AbstractUiTest):
    """UI 4.2: A failed generation shows that the quiz could not be assembled."""

    def test_should_show_assemble_error_and_keep_list(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        quiz_browser.and_the_quiz_tutor_will_fail()
        before = quiz_browser.quizzes.list(quiz_browser.signed_in.token)
        assert before.status_code == 200
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_create()
        quiz_screen.when_the_person_fills_create("cells", 5)
        quiz_screen.when_the_person_generates_expecting_error()
        quiz_screen.then_assemble_error_is_shown()
        after = quiz_browser.quizzes.list(quiz_browser.signed_in.token)
        assert after.body == before.body
