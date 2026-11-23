import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestCreateOpensTheForm(AbstractUiTest):
    """UI 6.1: Create opens the form."""

    def test_should_open_the_form_from_header_and_tile(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_create()
        quiz_screen.then_create_form_is_shown()
        quiz_screen.when_the_person_goes_back_to_the_list()
        quiz_screen.when_the_person_opens_create_via_tile()
        quiz_screen.then_create_form_is_shown()
