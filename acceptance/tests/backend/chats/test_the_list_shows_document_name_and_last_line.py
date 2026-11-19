import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTheListShowsDocumentNameAndLastLine(AbstractBackendTest):
    """The list shows this person's document name and last line, newest first.

    Given a signed-in person with two chats, the newer one spoken in last
    And a neighbour with a chat of their own
    When the person reads the chat list
    Then each row shows that chat's document name and the last person line
    And a chat with no person line has no preview
    And the newer chat is first
    And the neighbour's chat is absent
    And every chat this person owns is listed
    """

    def test_should_list_own_chats_with_document_name_and_preview(self, chats):
        chats.given_a_signed_in_person_with_two_chats_the_newer_one_spoken_in_last()
        chats.and_a_neighbour_with_a_chat_of_their_own()
        chats.when_the_person_reads_the_chat_list()
        chats.then_the_chat_list_shows_document_names_previews_and_owner_order()
