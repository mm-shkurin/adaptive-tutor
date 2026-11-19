from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

CHAT_TAB = (By.CSS_SELECTOR, "[data-testid='chat-tab']")
CHAT_PAGE = (By.CSS_SELECTOR, "[data-testid='chat-page']")
CHAT_LIST = (By.CSS_SELECTOR, "[data-testid='chat-list']")
CHAT_LIST_DOCUMENT = (By.CSS_SELECTOR, "[data-testid='chat-list-document']")
CHAT_LIST_PREVIEW = (By.CSS_SELECTOR, "[data-testid='chat-list-preview']")
CHAT_THREAD = (By.CSS_SELECTOR, "[data-testid='chat-thread']")
CHAT_THREAD_EMPTY = (By.CSS_SELECTOR, "[data-testid='chat-thread-empty']")
PERSON_LINE = (By.CSS_SELECTOR, "[data-testid='chat-person-line']")
TUTOR_LINE = (By.CSS_SELECTOR, "[data-testid='chat-tutor-line']")
LINE_TEXT = (By.CSS_SELECTOR, "[data-testid='chat-line-text']")
LINE_PAGE = (By.CSS_SELECTOR, "[data-testid='chat-line-page']")
LINE_MODEL = (By.CSS_SELECTOR, "[data-testid='chat-line-model']")
SOURCE_CARD = (By.CSS_SELECTOR, "[data-testid='chat-source-card']")
SOURCE_PAGE = (By.CSS_SELECTOR, "[data-testid='chat-source-page']")
SOURCE_TEXT = (By.CSS_SELECTOR, "[data-testid='chat-source-text']")
CHAT_NEW = (By.CSS_SELECTOR, "[data-testid='chat-new']")
CHAT_INPUT = (By.CSS_SELECTOR, "[data-testid='chat-input']")
CHAT_SEND = (By.CSS_SELECTOR, "[data-testid='chat-send']")
CHAT_TELL = (By.CSS_SELECTOR, "[data-testid='chat-tell']")
CHAT_MODE_SOCRATIC = (By.CSS_SELECTOR, "[data-testid='chat-mode-socratic']")
CHAT_MODE_EXAMINER = (By.CSS_SELECTOR, "[data-testid='chat-mode-examiner']")
CHAT_CHOICES = (By.CSS_SELECTOR, "[data-testid='chat-choices']")
CHAT_GRADE = (By.CSS_SELECTOR, "[data-testid='chat-grade-label']")
CHAT_REPLY_FAILED = (By.CSS_SELECTOR, "[data-testid='chat-reply-failed']")
CHAT_WORKING = (By.CSS_SELECTOR, "[data-testid='chat-working']")
BOUND_DOCUMENT = (By.CSS_SELECTOR, "[data-testid='chat-bound-document']")
WAIT_SECONDS = 20

PERSON_QUESTION = "Что такое собственное число матрицы?"
TUTOR_ANSWER = "Собственное число — скаляр λ, для которого Av = λv."
SOURCE_TEXT_VALUE = "Число λ называется собственным числом квадратной матрицы A."
SOCRATIC_QUESTION = "What would you say photosynthesis needs?"
EXAMINER_QUESTION = "Which process uses light?"
RELEASE = "Photosynthesis needs light, water, and carbon dioxide."
MODEL = "qwen/qwen3-32b"
PAGE = 5


class ChatScreenStatements:
    def __init__(self, driver, app_url=None):
        self.driver = driver
        self.app_url = app_url
        self.wait = WebDriverWait(driver, WAIT_SECONDS)

    def when_the_person_opens_the_chat(self) -> None:
        self.wait.until(self._chat_tab, "no chat-tab").click()
        self.wait.until(self._chat_page, "no chat-page")

    def when_the_person_starts_a_new_chat(self) -> None:
        before = self._bound_document_text()
        self.wait.until(lambda driver: driver.find_element(*CHAT_NEW)).click()
        self.wait.until(self._thread_empty, "thread not empty after new chat")
        self._before_document = before

    def when_the_person_sends_a_question(self, text: str = PERSON_QUESTION) -> None:
        field = self.wait.until(lambda driver: driver.find_element(*CHAT_INPUT))
        field.clear()
        field.send_keys(text)
        self.wait.until(lambda driver: driver.find_element(*CHAT_SEND)).click()
        self.wait.until(self._tutor_visible, "no tutor line after send")

    def when_the_person_sends_a_question_that_fails(self, text: str = PERSON_QUESTION) -> None:
        field = self.wait.until(lambda driver: driver.find_element(*CHAT_INPUT))
        field.clear()
        field.send_keys(text)
        self.wait.until(lambda driver: driver.find_element(*CHAT_SEND)).click()
        self.wait.until(
            lambda driver: driver.find_elements(*CHAT_REPLY_FAILED),
            "no failure message after failed send",
        )

    def when_the_person_sends_while_the_reply_is_held(self, text: str = PERSON_QUESTION) -> None:
        field = self.wait.until(lambda driver: driver.find_element(*CHAT_INPUT))
        field.clear()
        field.send_keys(text)
        self.wait.until(lambda driver: driver.find_element(*CHAT_SEND)).click()
        self.wait.until(
            lambda driver: driver.find_elements(*CHAT_WORKING),
            "no working state while reply in flight",
        )

    def then_the_screen_shows_that_it_is_working_and_not_the_failure_message(self) -> None:
        working = self.driver.find_elements(*CHAT_WORKING)
        assert working and working[0].is_displayed()
        assert self.driver.find_elements(*CHAT_REPLY_FAILED) == []

    def then_the_list_row_shows_the_document_name_and_the_last_person_line(
        self, document_name: str, preview: str
    ) -> None:
        self.wait.until(self._list_ready, "no chat list")
        names = [el.text for el in self.driver.find_elements(*CHAT_LIST_DOCUMENT)]
        previews = [el.text for el in self.driver.find_elements(*CHAT_LIST_PREVIEW)]
        assert document_name in names
        assert preview in previews

    def then_the_thread_shows_the_person_line_the_tutor_line_the_model_and_the_page(
        self, person: str, tutor: str, model: str, page: int
    ) -> None:
        self.wait.until(self._tutor_visible, "no tutor line")
        person_texts = [
            el.find_element(*LINE_TEXT).text for el in self.driver.find_elements(*PERSON_LINE)
        ]
        tutor_el = self.driver.find_elements(*TUTOR_LINE)[-1]
        assert person in person_texts
        assert tutor_el.find_element(*LINE_TEXT).text == tutor
        assert tutor_el.find_element(*LINE_MODEL).text == model
        citation = tutor_el.find_element(*LINE_PAGE).text
        assert citation == f"страница {page}"
        assert "слайд" not in citation.lower()

    def then_the_sources_show_the_page_and_the_piece_text(self, page: int, text: str) -> None:
        cards = self.wait.until(lambda driver: driver.find_elements(*SOURCE_CARD))
        assert len(cards) >= 1
        page_labels = [el.text for el in self.driver.find_elements(*SOURCE_PAGE)]
        texts = [el.text for el in self.driver.find_elements(*SOURCE_TEXT)]
        assert f"страница {page}" in page_labels
        assert text in texts

    def then_the_citation_is_a_page_not_a_slide(self) -> None:
        citations = [el.text for el in self.driver.find_elements(*LINE_PAGE)]
        assert citations
        for citation in citations:
            assert citation.startswith("страница ")
            assert "слайд" not in citation.lower()

    def then_the_thread_is_empty(self) -> None:
        self.wait.until(self._thread_empty, "thread not empty")

    def then_the_chat_is_bound_to_the_selected_pdf(self, document_name: str) -> None:
        bound = self.wait.until(lambda driver: driver.find_element(*BOUND_DOCUMENT))
        assert bound.get_attribute("textContent") == document_name

    def then_the_tutor_line_appears_whole_with_the_model_and_the_page(
        self, tutor: str, model: str, page: int
    ) -> None:
        self.wait.until(self._tutor_visible, "no tutor line")
        tutor_el = self.driver.find_elements(*TUTOR_LINE)[-1]
        assert tutor_el.find_element(*LINE_TEXT).text == tutor
        assert tutor_el.find_element(*LINE_MODEL).text == model
        assert tutor_el.find_element(*LINE_PAGE).text == f"страница {page}"

    def when_the_person_sends_a_question_in_socratic_mode(self) -> None:
        self.wait.until(lambda driver: driver.find_element(*CHAT_MODE_SOCRATIC)).click()
        field = self.wait.until(lambda driver: driver.find_element(*CHAT_INPUT))
        field.clear()
        field.send_keys(PERSON_QUESTION)
        self.wait.until(lambda driver: driver.find_element(*CHAT_SEND)).click()
        self.wait.until(self._tutor_visible, "no tutor line after socratic send")

    def then_the_tutor_shows_a_question_without_a_page(self, text: str) -> None:
        self.wait.until(self._tutor_visible, "no tutor line")
        tutor_el = self.driver.find_elements(*TUTOR_LINE)[-1]
        assert tutor_el.find_element(*LINE_TEXT).text == text
        assert tutor_el.get_attribute("data-kind") == "withheld"
        assert tutor_el.find_elements(*LINE_PAGE) == []

    def when_the_person_sends_a_try(self, text: str = "I think it needs sunlight.") -> None:
        field = self.wait.until(lambda driver: driver.find_element(*CHAT_INPUT))
        field.clear()
        field.send_keys(text)
        self.wait.until(lambda driver: driver.find_element(*CHAT_SEND)).click()
        self.wait.until(self._reply_with_page, "no answer after try")

    def then_the_tutor_shows_the_answer_with_a_page(self, text: str, page: int) -> None:
        tutor_el = self.driver.find_elements(*TUTOR_LINE)[-1]
        assert tutor_el.find_element(*LINE_TEXT).text == text
        assert tutor_el.find_element(*LINE_PAGE).text == f"страница {page}"

    def when_the_person_uses_the_tell_control(self) -> None:
        before = len(self.driver.find_elements(*PERSON_LINE))
        self._person_count_before_tell = before
        self.wait.until(lambda driver: driver.find_element(*CHAT_TELL)).click()
        self.wait.until(self._reply_with_page, "no released answer after tell")

    def then_the_answer_with_a_page_is_shown_without_a_new_person_line(
        self, text: str, page: int
    ) -> None:
        tutor_el = self.driver.find_elements(*TUTOR_LINE)[-1]
        assert tutor_el.find_element(*LINE_TEXT).text == text
        assert tutor_el.find_element(*LINE_PAGE).text == f"страница {page}"
        assert len(self.driver.find_elements(*PERSON_LINE)) == self._person_count_before_tell

    def when_the_person_chooses_examiner(self) -> None:
        self.wait.until(lambda driver: driver.find_element(*CHAT_MODE_EXAMINER)).click()
        self.wait.until(self._choices_visible, "no examiner choices")

    def then_one_question_with_four_choices_is_shown_without_a_page(self, text: str) -> None:
        tutor_el = self.driver.find_elements(*TUTOR_LINE)[-1]
        assert tutor_el.find_element(*LINE_TEXT).text == text
        assert tutor_el.get_attribute("data-kind") == "question"
        assert tutor_el.find_elements(*LINE_PAGE) == []
        choices = tutor_el.find_elements(By.CSS_SELECTOR, "[data-testid^='chat-choice-']")
        assert len(choices) == 4

    def when_the_person_chooses_a_choice(self, choice_id: str = "c1") -> None:
        button = self.wait.until(
            lambda driver: driver.find_element(By.CSS_SELECTOR, f"[data-testid='chat-choice-{choice_id}']")
        )
        button.click()
        self.wait.until(self._grade_visible, "no grade after choice")

    def when_the_person_chooses_again(self, choice_id: str = "c2") -> None:
        button = self.wait.until(
            lambda driver: driver.find_element(
                By.CSS_SELECTOR, f"[data-testid='chat-choice-{choice_id}']"
            )
        )
        before = len(self.driver.find_elements(*CHAT_GRADE))
        button.click()
        self.wait.until(
            lambda driver: len(driver.find_elements(*CHAT_GRADE)) == before
            or len(driver.find_elements(*CHAT_GRADE)) == before + 1,
            "choice click did not settle",
        )

    def grade_labels(self) -> list[str]:
        return [el.text for el in self.driver.find_elements(*CHAT_GRADE)]

    def then_right_or_wrong_is_shown_with_the_page(self, page: int) -> None:
        grade = self.wait.until(lambda driver: driver.find_elements(*CHAT_GRADE))[-1]
        assert grade.text in ("Верно", "Неверно")
        tutor_lines = self.driver.find_elements(*TUTOR_LINE)
        graded = next(el for el in tutor_lines if el.get_attribute("data-kind") == "grade")
        assert graded.find_element(*LINE_PAGE).text == f"страница {page}"

    def then_an_academic_answer_with_a_page_is_shown(self, text: str, page: int) -> None:
        tutor_el = self.wait.until(self._reply_with_page, "no academic reply with page")
        assert tutor_el.find_element(*LINE_TEXT).text == text
        assert tutor_el.get_attribute("data-kind") in (None, "reply", "")
        assert tutor_el.find_element(*LINE_PAGE).text == f"страница {page}"
        assert tutor_el.find_elements(*CHAT_CHOICES) == []

    def then_the_new_person_line_is_shown(self, text: str) -> None:
        self.wait.until(
            lambda driver: any(
                el.find_element(*LINE_TEXT).text == text for el in driver.find_elements(*PERSON_LINE)
            ),
            "new person line missing",
        )
        texts = [el.find_element(*LINE_TEXT).text for el in self.driver.find_elements(*PERSON_LINE)]
        assert text in texts

    def then_the_persons_line_is_shown_without_a_tutor_line(self, text: str) -> None:
        self.wait.until(
            lambda driver: any(
                el.find_element(*LINE_TEXT).text == text for el in driver.find_elements(*PERSON_LINE)
            ),
            "person line missing after failed reply",
        )
        person_texts = [
            el.find_element(*LINE_TEXT).text for el in self.driver.find_elements(*PERSON_LINE)
        ]
        assert text in person_texts
        tutor_texts = [
            el.find_element(*LINE_TEXT).text for el in self.driver.find_elements(*TUTOR_LINE)
        ]
        assert text not in tutor_texts or all(
            el.get_attribute("data-kind") != "reply" for el in self.driver.find_elements(*TUTOR_LINE)
        )
        assert not any(
            el.find_elements(*LINE_PAGE) for el in self.driver.find_elements(*TUTOR_LINE)
        )

    def then_the_failure_message_is_shown(self, message: str) -> None:
        alert = self.wait.until(lambda driver: driver.find_element(*CHAT_REPLY_FAILED))
        assert alert.text == message

    def then_the_screen_is_not_left_spinning(self) -> None:
        assert self.driver.find_elements(By.CSS_SELECTOR, ".spinner") == []
        send = self.wait.until(lambda driver: driver.find_element(*CHAT_SEND))
        assert send.is_enabled()

    def then_the_quiz_list_does_not_contain_those_questions(self, texts: list[str]) -> None:
        link = self.wait.until(
            lambda driver: next(
                (
                    el
                    for el in driver.find_elements(By.CSS_SELECTOR, "nav.tabs a")
                    if "Викторины" in el.text
                ),
                False,
            )
        )
        link.click()
        self.wait.until(
            lambda driver: "Викторины" in driver.find_element(By.CSS_SELECTOR, "main h2").text
        )
        body = self.driver.find_element(By.CSS_SELECTOR, "main").text
        for text in texts:
            assert text not in body

    def _choices_visible(self, driver):
        elements = [el for el in driver.find_elements(*CHAT_CHOICES) if el.is_displayed()]
        return elements[-1] if elements else False

    def _grade_visible(self, driver):
        elements = [el for el in driver.find_elements(*CHAT_GRADE) if el.is_displayed()]
        return elements[-1] if elements else False

    def _reply_with_page(self, driver):
        for el in reversed(driver.find_elements(*TUTOR_LINE)):
            if el.find_elements(*LINE_PAGE):
                return el
        return False

    def _chat_tab(self, driver):
        elements = [el for el in driver.find_elements(*CHAT_TAB) if el.is_displayed()]
        return elements[0] if elements else False

    def _chat_page(self, driver):
        elements = driver.find_elements(*CHAT_PAGE)
        return elements[0] if elements and elements[0].is_displayed() else False

    def _list_ready(self, driver):
        return bool(driver.find_elements(*CHAT_LIST_DOCUMENT))

    def _thread_empty(self, driver):
        elements = driver.find_elements(*CHAT_THREAD_EMPTY)
        return elements[0] if elements and elements[0].is_displayed() else False

    def _tutor_visible(self, driver):
        elements = [el for el in driver.find_elements(*TUTOR_LINE) if el.is_displayed()]
        return elements[-1] if elements else False

    def _bound_document_text(self) -> str:
        elements = self.driver.find_elements(*BOUND_DOCUMENT)
        return elements[0].get_attribute("textContent") if elements else ""
