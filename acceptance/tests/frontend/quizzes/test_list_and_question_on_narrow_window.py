import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestListAndQuestionOnNarrowWindow(AbstractUiTest):
    """UI 1.6: The list and the question stay reachable on a narrow window."""

    def test_should_reach_list_and_question(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_on_an_unanswered_question()
        quiz_screen.driver.set_window_size(390, 844)
        quiz_screen.when_the_person_opens_the_quizzes()
        wait = WebDriverWait(quiz_screen.driver, 20)
        tab = wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='quizzes-tab']"))
        assert tab
        quiz_screen.when_the_person_opens_the_card()
        choices = wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='quiz-choice']"))
        assert len(choices) == 4
        assert choices[0].is_displayed()
