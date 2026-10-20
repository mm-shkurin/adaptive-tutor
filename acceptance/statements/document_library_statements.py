from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

HEADING = (By.XPATH, "//*[normalize-space(.)='Документы']")
DOCUMENTS_TAB = (By.LINK_TEXT, "Документы")
PDF_DOOR_TITLE = (By.CSS_SELECTOR, "[data-testid='pdf-door-title']")
PDF_DOOR_HINT = (By.CSS_SELECTOR, "[data-testid='pdf-door-hint']")
PRESENTATION_DOOR = (By.CSS_SELECTOR, "[data-testid='presentation-door']")
DOCUMENT_LIST = (By.CSS_SELECTOR, "[data-testid='document-list']")
WAIT_SECONDS = 20


class DocumentLibraryStatements:
    def __init__(self, driver):
        self.driver = driver

    def when_the_person_opens_documents(self) -> None:
        WebDriverWait(self.driver, WAIT_SECONDS).until(self._documents_tab).click()
        WebDriverWait(self.driver, WAIT_SECONDS).until(self._documents_heading)

    def then_the_heading_is_documents(self) -> None:
        heading = WebDriverWait(self.driver, WAIT_SECONDS).until(self._documents_heading)
        assert heading.is_displayed()
        assert heading.text == "Документы"

    def then_the_pdf_door_reads_upload_pdf(self) -> None:
        self._assert_visible_text(PDF_DOOR_TITLE, "Загрузить PDF")

    def then_the_pdf_door_reads_the_size_hint(self) -> None:
        self._assert_visible_text(PDF_DOOR_HINT, "до 50 MB · парсинг и индексация")

    def then_the_presentation_door_reads_create_presentation(self) -> None:
        self._assert_visible_text(PRESENTATION_DOOR, "Создать презентацию")

    def then_the_list_reads_no_materials(self) -> None:
        self._assert_visible_text(DOCUMENT_LIST, "Пока нет материалов")

    def _documents_tab(self, driver):
        for element in driver.find_elements(*DOCUMENTS_TAB):
            if element.is_displayed():
                return element
        return False

    def _documents_heading(self, driver):
        for element in driver.find_elements(*HEADING):
            if element.tag_name == "h2" and element.is_displayed():
                return element
        return False

    def _assert_visible_text(self, locator, expected: str) -> None:
        found = [element for element in self.driver.find_elements(*locator) if element.is_displayed()]
        assert len(found) == 1
        assert found[0].is_displayed()
        assert found[0].text == expected
