from uuid import uuid4

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.abstract_ui_test import AbstractUiTest

JPEG = b"\xff\xd8\xff" + b"\x00" * 64


@pytest.mark.frontend
class TestPresentationIndexShowsReadyRow(AbstractUiTest):
    """UI 1.4: After index the documents list shows a ready presentation row

    Given a signed-in person with a ready-indexed presentation
    When the person opens documents
    Then the list shows a ready presentation row
    """

    def test_should_show_ready_presentation_on_documents(
        self, signed_in_browser, document_library
    ):
        token = signed_in_browser._open_session("ada@example.test", "Ada")
        http = signed_in_browser.sessions.http
        headers = {"Authorization": f"Bearer {token}"}
        created = http.post("/api/v1/presentations", headers=headers, json={"title": "LinAlg"})
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
                element.text == "Готов"
                for element in d.find_elements(By.CSS_SELECTOR, "[data-testid='document-status']")
                if element.is_displayed()
            )
        )
        names = [
            element.text
            for element in document_library.driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='document-name']"
            )
            if element.is_displayed()
        ]
        assert "LinAlg" in names
