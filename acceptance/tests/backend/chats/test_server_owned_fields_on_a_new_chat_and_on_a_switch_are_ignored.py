import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestServerOwnedFieldsOnANewChatAndOnASwitchAreIgnored(AbstractBackendTest):
    """Server-owned fields on a new chat and on a switch are ignored.

    Scenario Outline:
    Given a signed-in person with a ready PDF
    When the person <binds> and names an owner, an id, a creation time, a role, and a preview
    Then the chat belongs to the signed-in person
    And the id, the creation time, the role, and the preview are the ones the server stored
    """

    def test_should_ignore_server_owned_fields_when_starting_a_chat(self, chats):
        chats.given_a_signed_in_person_with_a_ready_pdf()
        chats.when_the_person_starts_a_chat_on_that_pdf_naming_server_owned_fields()
        chats.then_server_owned_bind_fields_are_ignored()

    def test_should_ignore_server_owned_fields_when_opening_a_chat(self, chats):
        chats.given_a_signed_in_person_with_a_ready_pdf()
        chats.when_the_person_opens_a_chat_for_that_pdf_naming_server_owned_fields()
        chats.then_server_owned_bind_fields_are_ignored()
