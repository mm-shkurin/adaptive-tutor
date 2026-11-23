import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestEmptyListShowsTheCreateEntry(AbstractUiTest):
    """UI 1.1: An empty list shows the create entry."""

    def test_should_show_empty_list_and_create_entry(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_no_quiz()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.then_the_empty_list_and_create_entry_are_shown()
