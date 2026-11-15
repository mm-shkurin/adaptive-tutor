import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestNewChatBindsTheSelectedReadyPdf(AbstractBackendTest):
    """A new chat binds the selected ready PDF and starts empty.

    Given a signed-in person
    And a selected ready PDF that is older than another ready PDF
    When the person starts a chat on the selected PDF
    Then the chat is bound to the selected PDF
    And the thread is empty
    And the list row shows that PDF's name and no preview
    """

    def test_should_bind_the_selected_pdf_and_start_empty(self, chats):
        chats.given_a_signed_in_person()
        chats.given_a_selected_ready_pdf_that_is_older_than_another()
        chats.when_the_person_starts_a_chat_on_the_selected_pdf()
        chats.then_the_chat_is_bound_to_the_selected_pdf()
        chats.then_the_thread_is_empty()
        chats.then_the_list_row_shows_that_pdfs_name_and_no_preview()
