import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestCreateFormListsReadyPdfs(AbstractUiTest):
    """UI 1.7: The create form lists ready PDFs and defaults the count to five."""

    def test_should_list_ready_pdfs_and_default_to_five(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_create()
        quiz_screen.then_create_lists_ready_pdfs_and_defaults_to_five(quiz_browser.ready_names)
