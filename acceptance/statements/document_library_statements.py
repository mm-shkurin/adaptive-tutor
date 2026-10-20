from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

DOCUMENTS_TAB = (By.CSS_SELECTOR, "[data-testid='documents-tab']")
DOCUMENTS_HEADING = (By.CSS_SELECTOR, "[data-testid='documents-heading']")
PDF_DOOR_TITLE = (By.CSS_SELECTOR, "[data-testid='pdf-door-title']")
PDF_DOOR_HINT = (By.CSS_SELECTOR, "[data-testid='pdf-door-hint']")
PRESENTATION_DOOR = (By.CSS_SELECTOR, "[data-testid='presentation-door']")
DOCUMENT_LIST = (By.CSS_SELECTOR, "[data-testid='document-list']")
WAIT_SECONDS = 20

DOCUMENTS = "Документы"
UPLOAD_PDF = "Загрузить PDF"
SIZE_HINT = "до 50 MB · парсинг и индексация"
CREATE_PRESENTATION = "Создать презентацию"
NO_MATERIALS = "Пока нет материалов"


class DocumentLibraryStatements:
    def __init__(self, driver):
        self.driver = driver

    def when_the_person_opens_documents(self) -> None:
        WebDriverWait(self.driver, WAIT_SECONDS).until(
            self._documents_tab,
            "no documents-tab",
        ).click()
        WebDriverWait(self.driver, WAIT_SECONDS).until(
            self._documents_heading,
            "no documents-heading",
        )

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

    def _documents_tab(self, driver):
        return self._displayed_text(driver, DOCUMENTS_TAB, DOCUMENTS)

    def _documents_heading(self, driver):
        return self._displayed(driver, DOCUMENTS_HEADING)

    def _displayed(self, driver, locator):
        for element in driver.find_elements(*locator):
            if element.is_displayed():
                return element
        return False

    def _displayed_text(self, driver, locator, expected: str):
        for element in driver.find_elements(*locator):
            if element.is_displayed() and element.text == expected:
                return element
        return False

    def _assert_visible_text(self, locator, expected: str) -> None:
        found = [element for element in self.driver.find_elements(*locator) if element.is_displayed()]
        assert len(found) == 1
        assert found[0].is_displayed()
        assert found[0].text == expected
