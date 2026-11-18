import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestServerOwnedFieldsOnASendAreIgnored(AbstractBackendTest):
    """Server-owned fields on a send are ignored.

    Given a signed-in person with an askable chat
    When the person sends a line that also names an owner, a page, a source, a role, and whether a grade is correct
    Then the chat still belongs to the signed-in person
    And the page and the sources are the retrieved piece's
    And the grade flag in the request is not the stored grade
    And the role in the request is not stored
    And the line id and the document id are the ones the server stored
    """

    def test_should_ignore_client_owned_fields_on_send(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_person_sends_a_line_that_also_names_server_owned_fields()
        chats.then_server_owned_send_fields_are_ignored()
