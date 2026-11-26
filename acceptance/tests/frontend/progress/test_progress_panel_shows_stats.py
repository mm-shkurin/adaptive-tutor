import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestProgressPanelShowsStats(AbstractUiTest):
    """UI 3.1: Progress panel shows four stats and topic nodes

    Given a signed-in person
    When the person opens progress
    Then the four stats are visible
    And the topic-nodes and weak-list cards are present
    """

    def test_should_show_stats_and_topic_cards(self, signed_in_browser, quiz_screen):
        signed_in_browser.given_a_signed_in_person_with_no_documents()
        quiz_screen.driver.get(f"{quiz_screen.app_url}/progress")
        wait = WebDriverWait(quiz_screen.driver, 20)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='progress']"))
        assert quiz_screen.driver.find_elements(By.CSS_SELECTOR, "[data-testid='prog-stats']")
        assert quiz_screen.driver.find_elements(By.CSS_SELECTOR, "[data-testid='prog-topic-nodes']")
        assert quiz_screen.driver.find_elements(By.CSS_SELECTOR, "[data-testid='prog-weak-list']")
        assert quiz_screen.driver.find_elements(By.CSS_SELECTOR, "[data-testid='prog-activity']")
