import tempfile
from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

DOCUMENTS_TAB = (By.CSS_SELECTOR, "[data-testid='documents-tab']")
DOCUMENTS_HEADING = (By.CSS_SELECTOR, "[data-testid='documents-heading']")
PDF_DOOR_TITLE = (By.CSS_SELECTOR, "[data-testid='pdf-door-title']")
PDF_DOOR_HINT = (By.CSS_SELECTOR, "[data-testid='pdf-door-hint']")
PRESENTATION_DOOR = (By.CSS_SELECTOR, "[data-testid='presentation-door']")
DOCUMENT_LIST = (By.CSS_SELECTOR, "[data-testid='document-list']")
DOCUMENT_ROW = (By.CSS_SELECTOR, "[data-testid='document-row']")
DOCUMENT_NAME = (By.CSS_SELECTOR, "[data-testid='document-name']")
DOCUMENT_META = (By.CSS_SELECTOR, "[data-testid='document-meta']")
DOCUMENT_STATUS = (By.CSS_SELECTOR, "[data-testid='document-status']")
DOCUMENT_FAILURE = (By.CSS_SELECTOR, "[data-testid='document-failure']")
PDF_UPLOAD_INPUT = (By.CSS_SELECTOR, "[data-testid='pdf-upload-input']")
LANDING = (By.CSS_SELECTOR, "[data-testid='landing']")
UPLOAD_REFUSAL = (By.CSS_SELECTOR, "[data-testid='upload-refusal']")
DOCUMENTS_ERROR = (By.CSS_SELECTOR, "[data-testid='documents-error']")
DOCUMENTS_RETRY = (By.CSS_SELECTOR, "[data-testid='documents-retry']")
DOCUMENTS_LOADING = (By.CSS_SELECTOR, "[data-testid='documents-loading']")
DOCUMENTS_EMPTY = (By.CSS_SELECTOR, "[data-testid='documents-empty']")
WAIT_SECONDS = 20

DOCUMENTS = "Документы"
UPLOAD_PDF = "Загрузить PDF"
SIZE_HINT = "до 50 MB · парсинг и индексация"
CREATE_PRESENTATION = "Создать презентацию"
NO_MATERIALS = "Пока нет материалов"
READY = "Готов"
WAITING = "Ждёт"
INDEXING = "В процессе"
FAILED = "Не удалось"
MATANALIZ = "Матанализ.pdf"
UPLOAD_NAME = "lecture.pdf"
NOT_A_PDF = "Файл не PDF. Список не изменился."
OVER_MAXIMUM = "Файл больше 50 МБ. Список не изменился."
PAGE_12 = "Не удалось прочитать страницу 12"
LOAD_ERROR = "Не удалось открыть документы."
RETRY = "Повторить"
MAX_PDF_BYTES = 52_428_800
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class DocumentLibraryStatements:
    def __init__(self, driver, app_url=None):
        self.driver = driver
        self.app_url = app_url
        self.wait = WebDriverWait(driver, WAIT_SECONDS)
        self._names_before = None

    def when_the_person_opens_documents(self) -> None:
        self.wait.until(self._documents_tab, "no documents-tab").click()
        self.wait.until(self._documents_heading, "no documents-heading")

    def when_the_person_uploads_a_valid_pdf(self) -> None:
        path = str(FIXTURES / "lecture.pdf")
        self.wait.until(lambda driver: driver.find_element(*PDF_UPLOAD_INPUT)).send_keys(path)
        self.wait.until(self._top_row_named(UPLOAD_NAME), "no uploaded row")

    def then_the_heading_is_documents(self) -> None:
        self._assert_visible_text(DOCUMENTS_HEADING, DOCUMENTS)

    def then_the_pdf_door_reads_upload_pdf(self) -> None:
        self._assert_visible_text(PDF_DOOR_TITLE, UPLOAD_PDF)

    def then_the_pdf_door_reads_the_size_hint(self) -> None:
        self._assert_visible_text(PDF_DOOR_HINT, SIZE_HINT)

    def then_the_presentation_door_reads_create_presentation(self) -> None:
        self._assert_visible_text(PRESENTATION_DOOR, CREATE_PRESENTATION)

    def then_the_list_reads_no_materials(self) -> None:
        self._assert_visible_text(DOCUMENT_LIST, NO_MATERIALS)

    def then_the_row_shows_matanaliz(self) -> None:
        names = [element.text for element in self._visible(DOCUMENT_NAME)]
        assert MATANALIZ in names

    def then_the_row_shows_size_pages_and_pieces(self, size_bytes: int, page_count: int, piece_count: int) -> None:
        megabytes = f"{size_bytes / (1024 * 1024):.1f} MB"
        expected = f"{megabytes} · {page_count} стр. · {piece_count} чанков"
        metas = [element.text for element in self._visible(DOCUMENT_META)]
        assert expected in metas

    def then_the_row_shows_ready(self) -> None:
        statuses = [element.text for element in self._visible(DOCUMENT_STATUS)]
        assert READY in statuses

    def then_the_row_shows_no_failure_reason(self) -> None:
        found = [element for element in self.driver.find_elements(*DOCUMENT_FAILURE) if element.is_displayed()]
        assert found == []

    def then_there_is_one_document_row(self) -> None:
        assert len(self._visible(DOCUMENT_ROW)) == 1

    def then_the_new_row_appears_at_the_top_as_waiting(self) -> None:
        self.wait.until(self._top_row_status(WAITING), "top row is not waiting")
        assert self._visible(DOCUMENT_NAME)[0].text == UPLOAD_NAME

    def then_the_earlier_ready_row_is_still_there(self) -> None:
        names = [element.text for element in self._visible(DOCUMENT_NAME)]
        assert names[0] == UPLOAD_NAME
        assert MATANALIZ in names
        assert len(self._visible(DOCUMENT_ROW)) == 2

    def then_the_new_row_later_shows_indexing_and_then_ready(self) -> None:
        self.wait.until(self._top_row_status(INDEXING), "top row never indexed")
        self.wait.until(self._top_row_status(READY), "top row never ready")

    def when_the_guest_opens_documents(self) -> None:
        self.driver.get(f"{self.app_url}/documents")
        self.wait.until(self._landing, "no landing")

    def then_the_guest_sees_the_landing(self) -> None:
        found = self._visible(LANDING)
        assert len(found) == 1
        assert found[0].is_displayed()

    def then_no_document_list_is_shown(self) -> None:
        assert self._visible(DOCUMENT_LIST) == []

    def then_no_upload_door_is_shown(self) -> None:
        assert self.driver.find_elements(*PDF_DOOR_TITLE) == []
        assert self.driver.find_elements(*PDF_UPLOAD_INPUT) == []

    def when_the_person_opens_documents_and_the_list_fails(self) -> None:
        self.wait.until(self._documents_tab, "no documents-tab").click()
        self.wait.until(self._documents_error, "no documents-error")

    def then_the_screen_shows_an_error_and_a_way_to_try_again(self) -> None:
        self._assert_visible_text(DOCUMENTS_ERROR, LOAD_ERROR)
        self._assert_visible_text(DOCUMENTS_RETRY, RETRY)

    def then_the_screen_does_not_read_no_materials(self) -> None:
        assert self._visible(DOCUMENTS_EMPTY) == []
        assert self._visible(DOCUMENT_LIST) == []

    def then_it_does_not_spin_forever(self) -> None:
        assert self._visible(DOCUMENTS_LOADING) == []
        assert self._visible(DOCUMENTS_ERROR) != []

    def when_the_person_tries_again(self) -> None:
        error = self.wait.until(self._documents_error, "no documents-error")
        self.wait.until(self._documents_retry, "no documents-retry").click()
        self.wait.until(self._error_left(error), "error stayed mounted")
        self.wait.until(self._documents_error, "error did not return")

    def when_the_person_submits_a_file_that_is_not_a_pdf(self) -> None:
        self._choose_file(FIXTURES / "extracted.txt")
        self.wait.until(self._refusal_text(NOT_A_PDF), "no not-pdf refusal")

    def when_the_person_submits_a_pdf_over_the_maximum(self) -> None:
        self._choose_file(self._oversized_pdf())
        self.wait.until(self._refusal_text(OVER_MAXIMUM), "no size refusal")

    def then_the_screen_shows_the_file_is_not_a_pdf(self) -> None:
        self._assert_visible_text(UPLOAD_REFUSAL, NOT_A_PDF)

    def then_the_screen_shows_the_file_is_over_50_mb(self) -> None:
        self._assert_visible_text(UPLOAD_REFUSAL, OVER_MAXIMUM)

    def then_the_ready_document_is_still_the_only_row(self) -> None:
        self.then_there_is_one_document_row()
        self.then_the_row_shows_matanaliz()
        self.then_the_row_shows_ready()

    def then_the_row_shows_failed(self) -> None:
        self._assert_visible_text(DOCUMENT_STATUS, FAILED)

    def then_the_row_shows_that_page_12_could_not_be_read(self) -> None:
        self._assert_visible_text(DOCUMENT_FAILURE, PAGE_12)

    def when_the_person_activates_create_presentation(self) -> None:
        self._names_before = [element.text for element in self._visible(DOCUMENT_NAME)]
        self.driver.execute_script(
            """
            if (!window.__documentFetchWrapped) {
              window.__documentPosts = 0;
              window.__documentFetchWrapped = true;
              const orig = window.fetch;
              window.fetch = function(input, init) {
                const method = ((init && init.method) || 'GET').toUpperCase();
                const url = typeof input === 'string' ? input : (input && input.url) || '';
                if (method === 'POST' && url.indexOf('/documents') !== -1) window.__documentPosts += 1;
                return orig.apply(this, arguments);
              };
            } else {
              window.__documentPosts = 0;
            }
            """
        )
        self._visible(PRESENTATION_DOOR)[0].click()

    def then_the_document_list_is_unchanged(self) -> None:
        names = [element.text for element in self._visible(DOCUMENT_NAME)]
        assert names == self._names_before

    def then_no_pdf_upload_starts(self) -> None:
        posts = self.driver.execute_script("return window.__documentPosts || 0")
        assert posts == 0
        assert self._visible(UPLOAD_REFUSAL) == []

    def _documents_tab(self, driver):
        return next((
            element for element in driver.find_elements(*DOCUMENTS_TAB)
            if element.is_displayed() and element.text == DOCUMENTS
        ), False)

    def _choose_file(self, path: Path) -> None:
        self.wait.until(lambda driver: driver.find_element(*PDF_UPLOAD_INPUT)).send_keys(str(path))

    def _oversized_pdf(self) -> Path:
        path = Path(tempfile.gettempdir()) / "adaptivetutor-over-50mb.pdf"
        if not path.exists() or path.stat().st_size <= MAX_PDF_BYTES:
            with path.open("wb") as handle:
                handle.seek(MAX_PDF_BYTES)
                handle.write(b"\0")
        return path

    def _landing(self, driver):
        return next((element for element in driver.find_elements(*LANDING) if element.is_displayed()), False)

    def _documents_error(self, driver):
        return next((
            element for element in driver.find_elements(*DOCUMENTS_ERROR) if element.is_displayed()
        ), False)

    def _error_left(self, error):
        def _gone(driver):
            try:
                return not error.is_displayed()
            except StaleElementReferenceException:
                return True
        return _gone

    def _documents_retry(self, driver):
        return next((
            element for element in driver.find_elements(*DOCUMENTS_RETRY) if element.is_displayed()
        ), False)

    def _refusal_text(self, expected: str):
        def _match(driver):
            found = self._visible(UPLOAD_REFUSAL)
            return bool(found) and found[0].text == expected
        return _match

    def _documents_heading(self, driver):
        return next((
            element for element in driver.find_elements(*DOCUMENTS_HEADING)
            if element.is_displayed()
        ), False)

    def _top_row_named(self, name: str):
        def _match(driver):
            names = [element.text for element in self._visible(DOCUMENT_NAME)]
            return bool(names) and names[0] == name
        return _match

    def _top_row_status(self, status: str):
        def _match(driver):
            statuses = [element.text for element in self._visible(DOCUMENT_STATUS)]
            return bool(statuses) and statuses[0] == status
        return _match

    def _visible(self, locator):
        return [element for element in self.driver.find_elements(*locator) if element.is_displayed()]

    def _assert_visible_text(self, locator, expected: str) -> None:
        found = self._visible(locator)
        assert len(found) == 1
        assert found[0].is_displayed()
        assert found[0].text == expected
