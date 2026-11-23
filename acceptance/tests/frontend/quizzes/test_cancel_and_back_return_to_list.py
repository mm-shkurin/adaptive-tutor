import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestCancelAndBackReturnToList(AbstractUiTest):
    """UI 6.2: Cancel and back return to the list."""

    def test_should_return_via_cancel_and_back(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_create()
        from selenium.webdriver.common.by import By

        quiz_screen.driver.find_element(By.CSS_SELECTOR, "[data-testid='quiz-cancel']").click()
        quiz_screen.then_list_is_shown()
        quiz_screen.when_the_person_opens_create()
        quiz_screen.when_the_person_goes_back_to_the_list()
        quiz_screen.then_list_is_shown()
