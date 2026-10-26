import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestReadyDocumentShowsFacts(AbstractUiTest):
    """UI Test Scenario 1.2: A ready document shows its name, size, pages, and piece count

    Given a signed-in person with a ready PDF named Матанализ.pdf
    When the person opens documents
    Then the row shows Матанализ.pdf
    And the row shows the size, the page count, and the piece count
    And the row shows «Готов»
    And the row shows no failure reason
    """

    def test_should_show_name_size_pages_and_piece_count(self, signed_in_browser, document_library):
        """UI Test Scenario 1.2: A ready document shows its name, size, pages, and piece count

        Given a signed-in person with a ready PDF named Матанализ.pdf
        When the person opens documents
        Then the row shows Матанализ.pdf
        And the row shows the size, the page count, and the piece count
        And the row shows «Готов»
        And the row shows no failure reason
        """
        signed_in_browser.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()
        document_library.when_the_person_opens_documents()
        document_library.then_there_is_one_document_row()
        document_library.then_the_row_shows_matanaliz()
        ready = signed_in_browser.ready_document.body
        document_library.then_the_row_shows_size_pages_and_pieces(
            ready["size_bytes"], ready["page_count"], ready["piece_count"]
        )
        document_library.then_the_row_shows_ready()
        document_library.then_the_row_shows_no_failure_reason()
