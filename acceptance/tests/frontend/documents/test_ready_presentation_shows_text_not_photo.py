from uuid import uuid4

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.abstract_ui_test import AbstractUiTest

JPEG = b"\xff\xd8\xff" + b"\x00" * 64


@pytest.mark.frontend
class TestReadyPresentationShowsTextNotPhoto(AbstractUiTest):
    """UI 2.1: Ready editor shows text not photo

    Given a ready presentation opened in the editor
    Then each slide shows recognized text
    And no slide photo is shown
    """

    def test_should_show_recognized_text_without_photo(
        self, signed_in_browser, document_library
    ):
        token = signed_in_browser._open_session("ada@example.test", "Ada")
        http = signed_in_browser.sessions.http
        headers = {"Authorization": f"Bearer {token}"}
        created = http.post(
            "/api/v1/presentations", headers=headers, json={"title": "ReadyText"}
        )
        assert created.status_code == 201
        presentation_id = created.json()["id"]
        added = http.post(
            f"/api/v1/presentations/{presentation_id}/slides",
            headers={**headers, "Idempotency-Key": str(uuid4())},
            files=[("images", ("slide.jpg", JPEG, "image/jpeg"))],
        )
        assert added.status_code == 200, added.text
        indexed = http.post(
            f"/api/v1/presentations/{presentation_id}/index",
            headers={**headers, "Idempotency-Key": str(uuid4())},
        )
        assert indexed.status_code == 202, indexed.text
        assert indexed.json()["status"] == "ready"
        document_library.when_the_person_opens_documents()
        wait = WebDriverWait(document_library.driver, 20)
        wait.until(
            lambda d: any(
                element.text == "ReadyText"
                for element in d.find_elements(
                    By.CSS_SELECTOR, "[data-testid='document-name']"
                )
                if element.is_displayed()
            )
        )
        row = next(
            element
            for element in document_library.driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='document-name']"
            )
            if element.is_displayed() and element.text == "ReadyText"
        )
        row.click()
        wait.until(
            lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='slide-card-text']")
        )
        text = document_library.driver.find_element(
            By.CSS_SELECTOR, "[data-testid='slide-card-text']"
        )
        assert text.tag_name == "textarea"
        assert "indexed text" in text.get_attribute("value")
        cards = document_library.driver.find_elements(
            By.CSS_SELECTOR, "[data-testid='slide-card']"
        )
        assert cards
        for card in cards:
            assert card.find_elements(By.TAG_NAME, "img") == []
            assert card.find_elements(By.CSS_SELECTOR, "img") == []
