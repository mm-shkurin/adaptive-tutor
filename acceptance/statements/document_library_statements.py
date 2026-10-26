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
WAIT_SECONDS = 20

DOCUMENTS = "Документы"
UPLOAD_PDF = "Загрузить PDF"
SIZE_HINT = "до 50 MB · парсинг и индексация"
CREATE_PRESENTATION = "Создать презентацию"
NO_MATERIALS = "Пока нет материалов"
READY = "Готов"
MATANALIZ = "Матанализ.pdf"


class DocumentLibraryStatements:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT_SECONDS)

    def when_the_person_opens_documents(self) -> None:
        self.wait.until(self._documents_tab, "no documents-tab").click()
        self.wait.until(self._documents_heading, "no documents-heading")

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
        self._assert_visible_text(DOCUMENT_NAME, MATANALIZ)

    def then_the_row_shows_size_pages_and_pieces(self, size_bytes: int, page_count: int, piece_count: int) -> None:
        megabytes = f"{size_bytes / (1024 * 1024):.1f} MB"
        expected = f"{megabytes} · {page_count} стр. · {piece_count} чанков"
        self._assert_visible_text(DOCUMENT_META, expected)

    def then_the_row_shows_ready(self) -> None:
        self._assert_visible_text(DOCUMENT_STATUS, READY)

    def then_the_row_shows_no_failure_reason(self) -> None:
        found = [element for element in self.driver.find_elements(*DOCUMENT_FAILURE) if element.is_displayed()]
        assert found == []

    def then_there_is_one_document_row(self) -> None:
        found = [element for element in self.driver.find_elements(*DOCUMENT_ROW) if element.is_displayed()]
        assert len(found) == 1

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

    def _assert_visible_text(self, locator, expected: str) -> None:
        found = [element for element in self.driver.find_elements(*locator) if element.is_displayed()]
        assert len(found) == 1
        assert found[0].is_displayed()
        assert found[0].text == expected
