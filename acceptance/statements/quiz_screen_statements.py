from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

QUIZZES_TAB = (By.CSS_SELECTOR, "[data-testid='quizzes-tab']")
QUIZ_PAGE = (By.CSS_SELECTOR, "[data-testid='quiz-page']")
QUIZ_EMPTY = (By.CSS_SELECTOR, "[data-testid='quiz-empty']")
QUIZ_CREATE_OPEN = (By.CSS_SELECTOR, "[data-testid='quiz-create-open']")
QUIZ_CREATE_TILE = (By.CSS_SELECTOR, "[data-testid='quiz-create-tile']")
QUIZ_CREATE = (By.CSS_SELECTOR, "[data-testid='quiz-create']")
QUIZ_DOCUMENT = (By.CSS_SELECTOR, "[data-testid='quiz-document']")
QUIZ_DOCUMENT_OPTION = (By.CSS_SELECTOR, "[data-testid='quiz-document-option']")
QUIZ_TOPIC = (By.CSS_SELECTOR, "[data-testid='quiz-topic']")
QUIZ_COUNT = (By.CSS_SELECTOR, "[data-testid='quiz-count']")
QUIZ_GENERATE = (By.CSS_SELECTOR, "[data-testid='quiz-generate']")
QUIZ_QUESTION = (By.CSS_SELECTOR, "[data-testid='quiz-question']")
QUIZ_CHOICE = (By.CSS_SELECTOR, "[data-testid='quiz-choice']")
QUIZ_NEXT = (By.CSS_SELECTOR, "[data-testid='quiz-next']")
QUIZ_REVEAL = (By.CSS_SELECTOR, "[data-testid='quiz-reveal']")
QUIZ_GRADE = (By.CSS_SELECTOR, "[data-testid='quiz-grade']")
QUIZ_CITE_PAGE = (By.CSS_SELECTOR, "[data-testid='quiz-reveal'] [data-testid='quiz-page']")
QUIZ_RESULT = (By.CSS_SELECTOR, "[data-testid='quiz-result']")
QUIZ_SCORE = (By.CSS_SELECTOR, "[data-testid='quiz-score']")
QUIZ_REVIEW = (By.CSS_SELECTOR, "[data-testid='quiz-review']")
QUIZ_PLAY_AGAIN = (By.CSS_SELECTOR, "[data-testid='quiz-play-again']")
QUIZ_BACK = (By.CSS_SELECTOR, "[data-testid='quiz-back']")
QUIZ_CARD = (By.CSS_SELECTOR, "[data-testid='quiz-card']")
QUIZ_CARD_SCORE = (By.CSS_SELECTOR, "[data-testid='quiz-card-score']")
QUIZ_LOADING = (By.CSS_SELECTOR, "[data-testid='quiz-loading']")
WAIT_SECONDS = 20


class QuizScreenStatements:
    def __init__(self, driver, app_url=None):
        self.driver = driver
        self.app_url = app_url
        self.wait = WebDriverWait(driver, WAIT_SECONDS)

    def when_the_person_opens_the_quizzes(self) -> None:
        tabs = self.wait.until(lambda d: d.find_elements(*QUIZZES_TAB), "no quizzes-tab")
        visible = next((tab for tab in tabs if tab.is_displayed()), tabs[0])
        visible.click()
        self.wait.until(self._page_ready, "quizzes not ready")

    def when_the_person_opens_create(self) -> None:
        self.wait.until(lambda d: d.find_element(*QUIZ_CREATE_OPEN)).click()
        self.wait.until(lambda d: d.find_element(*QUIZ_CREATE), "no create form")

    def when_the_person_opens_create_via_tile(self) -> None:
        self.wait.until(lambda d: d.find_element(*QUIZ_CREATE_TILE)).click()
        self.wait.until(lambda d: d.find_element(*QUIZ_CREATE), "no create form")

    def when_the_person_fills_create(self, topic: str, count: int = 5) -> None:
        field = self.wait.until(lambda d: d.find_element(*QUIZ_TOPIC))
        field.clear()
        field.send_keys(topic)
        Select(self.driver.find_element(*QUIZ_COUNT)).select_by_value(str(count))

    def when_the_person_generates(self) -> None:
        self.wait.until(lambda d: d.find_element(*QUIZ_GENERATE)).click()
        self.wait.until(lambda d: d.find_elements(*QUIZ_QUESTION), "no question")

    def when_the_person_chooses_choice(self, index: int = 0) -> None:
        choices = self.wait.until(lambda d: d.find_elements(*QUIZ_CHOICE))
        choices[index].click()
        self.wait.until(lambda d: d.find_elements(*QUIZ_REVEAL), "no reveal")

    def when_the_person_goes_next(self) -> None:
        self.wait.until(lambda d: d.find_element(*QUIZ_NEXT)).click()

    def when_the_person_plays_again(self) -> None:
        self.wait.until(lambda d: d.find_element(*QUIZ_PLAY_AGAIN)).click()
        self.wait.until(lambda d: d.find_elements(*QUIZ_QUESTION), "no question after replay")

    def when_the_person_goes_back_to_the_list(self) -> None:
        back = self.wait.until(
            lambda d: d.find_elements(*QUIZ_BACK) or d.find_elements((By.CSS_SELECTOR, "[data-testid='quiz-back-to-list']")),
            "no back control",
        )[0]
        back.click()
        self.wait.until(self._list_ready, "list not ready")

    def when_the_person_opens_the_card(self) -> None:
        self.wait.until(lambda d: d.find_elements(*QUIZ_CARD))[0].click()
        self.wait.until(
            lambda d: d.find_elements(*QUIZ_QUESTION) or d.find_elements(*QUIZ_RESULT),
            "quiz detail missing",
        )

    def then_the_empty_list_and_create_entry_are_shown(self) -> None:
        empty = self.wait.until(lambda d: d.find_element(*QUIZ_EMPTY))
        assert empty.is_displayed()
        assert empty.text == "Пока нет викторин."
        assert self.driver.find_element(*QUIZ_CREATE_OPEN).is_displayed()
        assert self.driver.find_element(*QUIZ_CREATE_TILE).is_displayed()
        assert "мин" not in self.driver.find_element(*QUIZ_PAGE).text.lower()
        assert "источник" not in self.driver.find_element(*QUIZ_PAGE).text.lower()
        assert not self.driver.find_elements(*QUIZ_LOADING)

    def then_create_lists_ready_pdfs_and_defaults_to_five(self, names: list[str]) -> None:
        options = self.wait.until(lambda d: d.find_elements(*QUIZ_DOCUMENT_OPTION))
        shown = [option.text for option in options]
        for name in names:
            assert name in shown
        assert Select(self.driver.find_element(*QUIZ_COUNT)).first_selected_option.get_attribute(
            "value"
        ) == "5"
        values = [option.get_attribute("value") for option in Select(self.driver.find_element(*QUIZ_COUNT)).options]
        assert values == ["3", "5", "8"]
        assert not self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='quiz-model']")

    def then_four_choices_hide_page_and_skip(self) -> None:
        choices = self.wait.until(lambda d: d.find_elements(*QUIZ_CHOICE))
        assert len(choices) == 4
        assert not self.driver.find_elements(*QUIZ_REVEAL)
        assert not self.driver.find_elements(*QUIZ_CITE_PAGE)
        assert not self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='quiz-skip']")
        assert not self.driver.find_element(*QUIZ_NEXT).is_enabled()
        assert "слайд" not in self.driver.find_element(*QUIZ_PAGE).text.lower()

    def then_choice_shows_grade_and_page(self) -> None:
        assert self.wait.until(lambda d: d.find_element(*QUIZ_GRADE)).is_displayed()
        assert self.driver.find_element(*QUIZ_CITE_PAGE).is_displayed()
        assert self.driver.find_element(*QUIZ_NEXT).is_enabled()

    def then_result_shows_score_and_review(self) -> None:
        assert self.wait.until(lambda d: d.find_element(*QUIZ_RESULT)).is_displayed()
        assert self.driver.find_element(*QUIZ_SCORE).is_displayed()
        assert self.driver.find_element(*QUIZ_REVIEW).is_displayed()
        assert self.driver.find_element(*QUIZ_PLAY_AGAIN).is_displayed()

    def then_first_question_is_shown(self) -> None:
        assert self.wait.until(lambda d: d.find_elements(*QUIZ_QUESTION))
        assert not self.driver.find_elements(*QUIZ_REVEAL)

    def then_card_keeps_previous_score(self) -> None:
        self.wait.until(lambda d: d.find_elements(*QUIZ_CARD_SCORE))
        assert self.driver.find_element(*QUIZ_CARD_SCORE).is_displayed()

    def then_create_form_is_shown(self) -> None:
        assert self.wait.until(lambda d: d.find_element(*QUIZ_CREATE)).is_displayed()

    def then_list_is_shown(self) -> None:
        self.wait.until(self._list_ready, "list missing")

    def then_question_is_resumed(self) -> None:
        assert self.wait.until(lambda d: d.find_elements(*QUIZ_QUESTION))

    def _page_ready(self, driver) -> bool:
        return bool(driver.find_elements(*QUIZ_PAGE)) and not driver.find_elements(*QUIZ_LOADING)

    def _list_ready(self, driver) -> bool:
        return self._page_ready(driver) and (
            driver.find_elements(*QUIZ_EMPTY) or driver.find_elements(*QUIZ_CREATE_TILE)
        )
