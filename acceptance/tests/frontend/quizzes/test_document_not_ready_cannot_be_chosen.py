import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestDocumentNotReadyCannotBeChosen(AbstractUiTest):
    """UI 0.3: A document that is not ready cannot be chosen."""

    def test_should_list_only_ready_pdfs(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_ready_and_not_ready_pdfs()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_create()
        quiz_screen.then_create_lists_only_ready_pdfs(
            quiz_browser.ready_names, quiz_browser.not_ready_names
        )
