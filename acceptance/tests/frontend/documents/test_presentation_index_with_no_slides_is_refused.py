import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestPresentationIndexWithNoSlidesIsRefused(AbstractUiTest):
    """UI 1.3: Index with no slides stays on the editor with a refusal

    Given a signed-in person with an empty draft presentation open
    When the person activates index
    Then the editor stays open with a refusal
    """

    def test_should_keep_the_editor_and_show_refusal(self, signed_in_browser, document_library):
        signed_in_browser.given_a_signed_in_person_with_no_documents()
        document_library.when_the_person_opens_documents()
        document_library.when_the_person_activates_create_presentation()
        document_library.then_the_presentation_editor_is_open()
        document_library.driver.find_element(By.CSS_SELECTOR, "[data-testid='pres-index']").click()
        wait = WebDriverWait(document_library.driver, 20)
        wait.until(
            lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='pres-refusal']")
            and d.find_element(By.CSS_SELECTOR, "[data-testid='pres-refusal']").text
        )
        assert document_library.driver.find_elements(By.CSS_SELECTOR, "[data-testid='pres-title']")
