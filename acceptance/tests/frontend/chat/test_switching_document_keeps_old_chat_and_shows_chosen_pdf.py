import pytest

from statements.chat_screen_statements import PERSON_QUESTION
from statements.signed_in_browser_statements import READY_NAME, SECOND_NAME
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestSwitchingDocumentKeepsOldChatAndShowsChosenPdf(AbstractUiTest):
    """UI Test Scenario 2.2: Switching document keeps the old chat and shows the chosen PDF

    Given a signed-in person reading a chat that has a person line
    When the person switches to another ready PDF
    Then the old chat remains in the list with that person line
    And the thread shown is the chat for the PDF just chosen
    """

    def test_should_keep_old_chat_and_show_chosen_pdf(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_two_ready_pdfs_and_an_askable_chat()
        signed_in_browser.script_tutor(signed_in_browser.tutor_line)
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_a_question(PERSON_QUESTION)
        chat_screen.when_the_person_switches_to_another_ready_pdf(SECOND_NAME)
        chat_screen.then_the_list_row_shows_the_document_name_and_the_last_person_line(
            READY_NAME, PERSON_QUESTION
        )
        chat_screen.then_the_chat_is_bound_to_the_selected_pdf(SECOND_NAME)
        chat_screen.then_the_thread_is_empty()
