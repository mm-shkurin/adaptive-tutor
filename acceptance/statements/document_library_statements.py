from pathlib import Path

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
WAIT_SECONDS = 20

DOCUMENTS = "Документы"
UPLOAD_PDF = "Загрузить PDF"
SIZE_HINT = "до 50 MB · парсинг и индексация"
CREATE_PRESENTATION = "Создать презентацию"
NO_MATERIALS = "Пока нет материалов"
READY = "Готов"
WAITING = "Ждёт"
INDEXING = "В процессе"
MATANALIZ = "Матанализ.pdf"
UPLOAD_NAME = "lecture.pdf"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class DocumentLibraryStatements:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT_SECONDS)

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

    def _documents_tab(self, driver):
        return next((
            element for element in driver.find_elements(*DOCUMENTS_TAB)
            if element.is_displayed() and element.text == DOCUMENTS
        ), False)

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
