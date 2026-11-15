import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestNewChatWithNothingSelectedBindsNewestReadyPdf(AbstractBackendTest):
    """A new chat with nothing selected binds the newest ready PDF.

    Given a signed-in person with two ready PDFs and nothing selected
    And a neighbour who owns a newer ready PDF
    When the person starts a chat
    Then the chat is bound to the person's newer PDF
    And the neighbour's PDF is not bound
    And the thread is empty
    """

    def test_should_bind_the_persons_newest_ready_pdf(self, chats):
        chats.given_a_signed_in_person_with_two_ready_pdfs_and_nothing_selected()
        chats.and_a_neighbour_who_owns_a_newer_ready_pdf()
        chats.when_the_person_starts_a_chat()
        chats.then_the_chat_is_bound_to_the_persons_newer_pdf()
        chats.then_the_neighbours_pdf_is_not_bound()
        chats.then_the_thread_is_empty()
