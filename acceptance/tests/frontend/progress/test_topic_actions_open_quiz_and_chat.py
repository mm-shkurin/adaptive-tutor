import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from statements.quiz_browser_statements import valid_quiz_body
from tests.frontend.abstract_ui_test import AbstractUiTest


def _finish_all_correct(quizzes, token, quiz_id):
    detail = quizzes.get(token, quiz_id).body
    while detail["status"] == "take":
        chosen = detail["questions"][detail["current_index"]]["choices"][0]["id"]
        assert quizzes.answer(token, quiz_id, chosen).status_code == 200
        advanced = quizzes.advance(token, quiz_id)
        assert advanced.status_code == 200
        detail = advanced.body
    return detail


@pytest.mark.frontend
class TestTopicActionsOpenQuizAndChat(AbstractUiTest):
    """UI 3.3: Topic actions open quiz create and chat

    Given a topic detail on Progress
    When the person activates «Викторина по теме»
    Then quiz create for that topic and material is started
    When the person activates «Спросить в чате»
    Then chat for that material is shown
    """

    def test_should_open_quiz_create_then_chat(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        token = quiz_browser.signed_in.token
        document_id = quiz_browser.signed_in.ready_document.body["id"]
        quizzes = quiz_browser.quizzes
        scripted = quizzes.script_tutor(token, valid_quiz_body(3))
        assert scripted.status_code == 204
        created = quizzes.create(token, document_id, "Matrices", 3)
        assert created.status_code == 201, created.body
        _finish_all_correct(quizzes, token, created.body["id"])
        driver = quiz_screen.driver
        driver.get(f"{quiz_screen.app_url}/progress")
        wait = WebDriverWait(driver, 20)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='progress']"))
        _click_topic_named(wait, driver, "Matrices")
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='topic-quiz']"))
        driver.find_element(By.CSS_SELECTOR, "[data-testid='topic-quiz']").click()
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='quiz-create']"))
        assert "/quizzes/new" in driver.current_url
        topic_field = driver.find_element(By.CSS_SELECTOR, "[data-testid='quiz-topic']")
        assert topic_field.get_attribute("value") == "Matrices"
        selected = driver.find_element(By.CSS_SELECTOR, "[data-testid='quiz-document']")
        assert selected.get_attribute("value") == document_id
        driver.get(f"{quiz_screen.app_url}/progress")
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='progress']"))
        _click_topic_named(wait, driver, "Matrices")
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='topic-chat']"))
        driver.find_element(By.CSS_SELECTOR, "[data-testid='topic-chat']").click()
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='chat-page']"))
        assert "/chat" in driver.current_url
        bound = wait.until(
            lambda d: d.find_elements(By.CSS_SELECTOR, "[data-testid='chat-bound-document']")
        )
        assert bound


def _click_topic_named(wait, driver, name: str) -> None:
    topic = wait.until(
        lambda d: next(
            (
                element
                for element in d.find_elements(
                    By.CSS_SELECTOR, "button[data-testid^='prog-topic-']"
                )
                if element.is_displayed() and name in element.text
            ),
            False,
        )
    )
    topic.click()
