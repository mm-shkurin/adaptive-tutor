from uuid import uuid4

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.abstract_ui_test import AbstractUiTest

JPEG = b"\xff\xd8\xff" + b"\x00" * 64


@pytest.mark.frontend
class TestFailedPresentationShowsRetryInEditor(AbstractUiTest):
    """Failed index keeps the editor usable with a retry CTA.

    Given a signed-in person with a failed presentation
    When the person opens it from documents
    Then the editor shows the failure and a retry index label
    """

    def test_should_show_failure_banner_and_retry_label(
        self, signed_in_browser, document_library
    ):
        token = signed_in_browser._open_session("ada@example.test", "Ada")
        http = signed_in_browser.sessions.http
        headers = {"Authorization": f"Bearer {token}"}
        created = http.post("/api/v1/presentations", headers=headers, json={"title": "FailDeck"})
        assert created.status_code == 201
        presentation_id = created.json()["id"]
        added = http.post(
            f"/api/v1/presentations/{presentation_id}/slides",
            headers={**headers, "Idempotency-Key": str(uuid4())},
            files=[("images", ("slide.jpg", JPEG, "image/jpeg"))],
        )
        assert added.status_code == 200, added.text
        assert http.post("/acceptance/presentations/ocr-fail").status_code == 200
        indexed = http.post(
            f"/api/v1/presentations/{presentation_id}/index",
            headers={**headers, "Idempotency-Key": str(uuid4())},
        )
        assert indexed.status_code == 202, indexed.text
        assert indexed.json()["status"] == "failed"
        document_library.when_the_person_opens_documents()
        wait = WebDriverWait(document_library.driver, 20)
        wait.until(
            lambda d: any(
                element.text == "FailDeck"
                for element in d.find_elements(By.CSS_SELECTOR, "[data-testid='document-name']")
                if element.is_displayed()
            )
        )
        row = next(
            element
            for element in document_library.driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='document-name']"
            )
            if element.is_displayed() and element.text == "FailDeck"
        )
        row.click()
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='pres-index-failure']"))
        banner = document_library.driver.find_element(
            By.CSS_SELECTOR, "[data-testid='pres-index-failure']"
        ).text
        assert "ocr refused" in banner
        assert (
            document_library.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='pres-index']"
            ).text
            == "Повторить индексацию"
        )
