import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestPaperclipOpensDocumentsAndAddsNoDocument(AbstractUiTest):
    """UI Test Scenario 2.3: The paperclip opens Documents and adds no document

    Given a signed-in person on the chat
    When the person uses the paperclip
    Then Documents is shown
    And no document is added
    """

    def test_should_open_documents_without_adding(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        before = signed_in_browser.document_count()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_uses_the_paperclip()
        chat_screen.then_documents_is_shown()
        signed_in_browser.then_no_document_was_added(before)
