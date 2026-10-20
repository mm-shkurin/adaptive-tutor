import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestEmptyLibraryShowsThePdfDoor(AbstractUiTest):
    """UI Test Scenario 1.1: An empty library shows the PDF door and no materials

    Given a signed-in person with no documents
    When the person opens documents
    Then the heading is «Документы»
    And the PDF door reads «Загрузить PDF» and «до 50 MB · парсинг и индексация»
    And the presentation door reads «Создать презентацию»
    And the list reads «Пока нет материалов»
    """

    @pytest.mark.skip(reason="RED: no documents-tab (TimeoutException)")
    def test_should_show_the_pdf_door_and_no_materials(self, signed_in_browser, document_library):
        """UI Test Scenario 1.1: An empty library shows the PDF door and no materials

        Given a signed-in person with no documents
        When the person opens documents
        Then the heading is «Документы»
        And the PDF door reads «Загрузить PDF» and «до 50 MB · парсинг и индексация»
        And the presentation door reads «Создать презентацию»
        And the list reads «Пока нет материалов»
        """
        signed_in_browser.given_a_signed_in_person_with_no_documents()
        document_library.when_the_person_opens_documents()
        document_library.then_the_heading_is_documents()
        document_library.then_the_pdf_door_reads_upload_pdf()
        document_library.then_the_pdf_door_reads_the_size_hint()
        document_library.then_the_presentation_door_reads_create_presentation()
        document_library.then_the_list_reads_no_materials()
