import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from statements.quiz_browser_statements import valid_quiz_body
from tests.frontend.abstract_ui_test import AbstractUiTest


def _finish_with_correct(quizzes, token, quiz_id, correct_count):
    detail = quizzes.get(token, quiz_id).body
    answered = 0
    while detail["status"] == "take":
        pick = 0 if answered < correct_count else 1
        chosen = detail["questions"][detail["current_index"]]["choices"][pick]["id"]
        assert quizzes.answer(token, quiz_id, chosen).status_code == 200
        advanced = quizzes.advance(token, quiz_id)
        assert advanced.status_code == 200
        detail = advanced.body
        answered += 1
    return detail


def _finish_topic(quiz_browser, document_id, topic, count, correct):
    token = quiz_browser.signed_in.token
    quizzes = quiz_browser.quizzes
    scripted = quizzes.script_tutor(token, valid_quiz_body(count))
    assert scripted.status_code == 204
    created = quizzes.create(token, document_id, topic, count)
    assert created.status_code == 201, created.body
    return _finish_with_correct(quizzes, token, created.body["id"], correct)


@pytest.mark.frontend
class TestWeakListMatchesBand(AbstractUiTest):
    """UI 3.2: Weak list matches the weak count band

    Given topics below and above 40%
    When the person opens Progress
    Then the weak list only includes topics below 40%
    And the weak count equals that list length
    """

    def test_should_list_only_topics_under_forty(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        first = quiz_browser.signed_in.ready_document.body["id"]
        listed = quiz_browser.signed_in.documents.list_documents(
            quiz_browser.signed_in.token
        )
        assert listed.status_code == 200
        second = next(
            item["id"]
            for item in listed.body["documents"]
            if item["id"] != first
        )
        _finish_topic(quiz_browser, first, "weak topic", 8, 2)
        _finish_topic(quiz_browser, second, "mid topic", 8, 4)
        _finish_topic(quiz_browser, first, "strong topic", 5, 4)
        quiz_screen.driver.get(f"{quiz_screen.app_url}/progress")
        wait = WebDriverWait(quiz_screen.driver, 20)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='progress']"))
        wait.until(
            lambda d: d.find_element(By.CSS_SELECTOR, "[data-testid='prog-weak-n']").text
            == "1"
        )
        weak_rows = [
            element
            for element in quiz_screen.driver.find_elements(
                By.CSS_SELECTOR, "[data-testid^='prog-weak-']"
            )
            if element.is_displayed()
            and _is_weak_topic_row(element.get_attribute("data-testid"))
        ]
        assert len(weak_rows) == 1
        assert "weak topic" in weak_rows[0].text
        assert "mid topic" not in weak_rows[0].text
        assert "strong topic" not in weak_rows[0].text
        names = " ".join(
            node.text
            for node in quiz_screen.driver.find_elements(
                By.CSS_SELECTOR, "button[data-testid^='prog-topic-']"
            )
            if node.is_displayed()
        )
        assert "weak topic" in names
        assert "mid topic" in names
        assert "strong topic" in names


def _is_weak_topic_row(test_id: str | None) -> bool:
    if not test_id or test_id in {"prog-weak-n", "prog-weak-list"}:
        return False
    return "mastery" not in test_id
