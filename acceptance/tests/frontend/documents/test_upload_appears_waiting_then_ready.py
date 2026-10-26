import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestUploadAppearsWaitingThenReady(AbstractUiTest):
    """UI Test Scenario 2.1: An accepted PDF appears as waiting and then becomes ready

    Given a signed-in person with a ready document
    When the person uploads a valid PDF
    Then the new row appears at the top
    And the new row shows «Ждёт»
    And the earlier row is still there
    And the new row later shows «В процессе» and then «Готов»
    """

    def test_should_show_waiting_then_indexing_then_ready(self, signed_in_browser, document_library):
        """UI Test Scenario 2.1: An accepted PDF appears as waiting and then becomes ready

        Given a signed-in person with a ready document
        When the person uploads a valid PDF
        Then the new row appears at the top
        And the new row shows «Ждёт»
        And the earlier row is still there
        And the new row later shows «В процессе» and then «Готов»
        """
        signed_in_browser.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()
        document_library.when_the_person_opens_documents()
        document_library.when_the_person_uploads_a_valid_pdf()
        document_library.then_the_new_row_appears_at_the_top_as_waiting()
        document_library.then_the_earlier_ready_row_is_still_there()
        signed_in_browser.when_indexing_is_released()
        document_library.then_the_new_row_later_shows_indexing_and_then_ready()
