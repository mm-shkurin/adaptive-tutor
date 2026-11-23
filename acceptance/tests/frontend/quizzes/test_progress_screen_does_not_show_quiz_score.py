import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestProgressScreenDoesNotShowQuizScore(AbstractUiTest):
    """UI 6.7: The progress screen does not show the quiz score."""

    def test_should_not_show_quiz_score_on_progress(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_a_finished_quiz()
        quiz_screen.when_the_person_opens_the_quizzes()
        score = quiz_screen.driver.find_element(By.CSS_SELECTOR, "[data-testid='quiz-card-score']").text
        quiz_screen.driver.get(f"{quiz_screen.app_url}/progress")
        wait = WebDriverWait(quiz_screen.driver, 20)
        wait.until(lambda d: "/progress" in d.current_url)
        body = quiz_screen.driver.find_element(By.TAG_NAME, "body").text
        assert score not in body
        assert "Прошлый результат" not in body
