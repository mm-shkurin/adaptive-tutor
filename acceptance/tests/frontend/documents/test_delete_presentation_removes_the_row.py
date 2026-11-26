import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestDeletePresentationRemovesTheRow(AbstractUiTest):
    """UI 2.2: Delete removes the row from Documents

    Given a signed-in person with a draft presentation
    When the person deletes it from the editor
    Then the documents list no longer shows that draft
    """

    def test_should_remove_the_draft_row(self, signed_in_browser, document_library):
        signed_in_browser.given_a_signed_in_person_with_no_documents()
        document_library.when_the_person_opens_documents()
        document_library.when_the_person_activates_create_presentation()
        document_library.then_the_presentation_editor_is_open()
        document_library.driver.execute_script("window.confirm = () => true")
        document_library.driver.find_element(By.CSS_SELECTOR, "[data-testid='pres-delete']").click()
        wait = WebDriverWait(document_library.driver, 20)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='presentation-door']"))
        assert document_library.driver.find_elements(By.CSS_SELECTOR, "[data-testid='pres-title']") == []
        names = [
            element.text
            for element in document_library.driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='document-name']"
            )
            if element.is_displayed()
        ]
        assert "Новая презентация" not in names
