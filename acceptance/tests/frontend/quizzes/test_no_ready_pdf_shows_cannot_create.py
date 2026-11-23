import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestNoReadyPdfShowsCannotCreate(AbstractUiTest):
    """UI 0.2: No ready PDF shows that a quiz cannot be created."""

    def test_should_show_needs_pdf_notice(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_no_quiz()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_create()
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(quiz_screen.driver, 20)
        notice = wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "[data-testid='quiz-needs-pdf']"))
        assert "готовый PDF" in notice.text
        generate = quiz_screen.driver.find_element(By.CSS_SELECTOR, "[data-testid='quiz-generate']")
        assert not generate.is_enabled()
