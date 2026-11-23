import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestReloadResumesSavedQuestion(AbstractUiTest):
    """UI 6.5: Reload resumes the saved question and does not grade again."""

    def test_should_resume_without_regrading(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_mid_quiz_after_one_answer()
        quiz_id = quiz_browser.quiz_id
        quiz_screen.driver.get(f"{quiz_screen.app_url}/quizzes/{quiz_id}")
        wait = WebDriverWait(quiz_screen.driver, 20)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='quiz-question']"))
        before = quiz_browser.quizzes.get(quiz_browser.signed_in.token, quiz_id).body
        quiz_screen.driver.refresh()
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='quiz-question']"))
        after = quiz_browser.quizzes.get(quiz_browser.signed_in.token, quiz_id).body
        assert after["current_index"] == before["current_index"] == 1
        assert after["questions"][0]["chosen_choice_id"] == before["questions"][0]["chosen_choice_id"]
        assert after["questions"][1]["chosen_choice_id"] is None
