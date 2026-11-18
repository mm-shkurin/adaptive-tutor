import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest

STATES = (
    "waiting",
    "indexing",
    "failed",
    "a status that is not a known document status",
)


@pytest.mark.backend
class TestADocumentThatIsNotReadyCannotBeBound(AbstractBackendTest):
    """A document that is not ready cannot be bound.

    Scenario Outline:
    Given a signed-in person
    And a document of theirs that is <state>
    When the person <binds> that document
    Then the bind is refused because the document is not ready
    And no chat is stored
    And the document status is unchanged
    """

    @pytest.mark.parametrize("state", STATES)
    def test_should_refuse_starting_a_chat_on_a_not_ready_document(self, chats, state):
        chats.given_a_signed_in_person_with_a_document_in_state(state)
        chats.when_the_person_starts_a_chat_on_that_document()
        chats.then_the_bind_is_refused_because_the_document_is_not_ready()
        chats.then_no_chat_is_stored()
        chats.then_the_document_status_is_unchanged()

    @pytest.mark.parametrize("state", STATES)
    def test_should_refuse_opening_a_chat_for_a_not_ready_document(self, chats, state):
        chats.given_a_signed_in_person_with_a_document_in_state(state)
        chats.when_the_person_opens_a_chat_for_that_document()
        chats.then_the_bind_is_refused_because_the_document_is_not_ready()
        chats.then_no_chat_is_stored()
        chats.then_the_document_status_is_unchanged()
