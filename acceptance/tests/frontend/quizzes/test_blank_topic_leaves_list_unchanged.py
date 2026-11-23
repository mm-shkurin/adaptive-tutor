import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestBlankTopicLeavesListUnchanged(AbstractUiTest):
    """UI 4.1: A blank topic leaves the list unchanged."""

    def test_should_refuse_blank_topic(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        quiz_screen.when_the_person_opens_the_quizzes()
        before = quiz_browser.quizzes.list(quiz_browser.signed_in.token)
        assert before.status_code == 200
        quiz_screen.when_the_person_opens_create()
        quiz_screen.when_the_person_fills_create("   ", 5)
        from selenium.webdriver.common.by import By

        quiz_screen.driver.find_element(By.CSS_SELECTOR, "[data-testid='quiz-generate']").click()
        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(quiz_screen.driver, 10)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='quiz-create']"))
        after = quiz_browser.quizzes.list(quiz_browser.signed_in.token)
        assert after.body == before.body
