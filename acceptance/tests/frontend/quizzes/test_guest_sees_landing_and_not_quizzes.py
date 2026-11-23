import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestGuestSeesLandingAndNotQuizzes(AbstractUiTest):
    """UI 0.1: A guest sees the landing and not the quizzes."""

    def test_should_show_landing_without_quizzes(self, signed_in_browser, quiz_screen):
        signed_in_browser.given_a_guest()
        signed_in_browser.driver.get(signed_in_browser.app_url)
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(signed_in_browser.driver, 20)
        landing = wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "[data-testid='landing']"))
        assert landing.is_displayed()
        signed_in_browser.driver.get(f"{signed_in_browser.app_url}/quizzes")
        wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "[data-testid='landing']"))
        assert not signed_in_browser.driver.find_elements(By.CSS_SELECTOR, "[data-testid='quiz-page']")
        assert not signed_in_browser.driver.find_elements(By.CSS_SELECTOR, "[data-testid='quizzes-tab']")
