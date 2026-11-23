import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestLeavingFormBeforeGenerateStoresNothing(AbstractUiTest):
    """UI 4.3: Leaving the form before generate stores nothing."""

    def test_should_store_nothing(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_create()
        quiz_screen.when_the_person_fills_create("cells", 5)
        quiz_screen.when_the_person_goes_back_to_the_list()
        listed = quiz_browser.quizzes.list(quiz_browser.signed_in.token)
        assert listed.status_code == 200
        assert listed.body == {"quizzes": []}
