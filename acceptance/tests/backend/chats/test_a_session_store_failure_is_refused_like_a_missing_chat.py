import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestASessionStoreFailureIsRefusedLikeAMissingChat(AbstractBackendTest):
    """A session store failure is refused like a missing chat.

    Scenario Outline:
    Given a signed-in person's session store fails
    When the person <asks>
    Then the refusal matches a missing chat
    And nothing is stored
    """

    def test_should_refuse_reading_the_chat_list(self, chats):
        chats.given_a_signed_in_persons_session_store_fails()
        chats.when_the_person_reads_the_chat_list_with_failed_session_store()
        chats.then_the_refusal_matches_a_missing_chat_for_session_store_failure()
        chats.then_nothing_is_stored_after_session_store_failure()

    def test_should_refuse_reading_a_chat(self, chats):
        chats.given_a_signed_in_persons_session_store_fails()
        chats.when_the_person_reads_a_chat_with_failed_session_store()
        chats.then_the_refusal_matches_a_missing_chat_for_session_store_failure()
        chats.then_nothing_is_stored_after_session_store_failure()

    def test_should_refuse_starting_a_chat(self, chats):
        chats.given_a_signed_in_persons_session_store_fails()
        chats.when_the_person_starts_a_chat_with_failed_session_store()
        chats.then_the_refusal_matches_a_missing_chat_for_session_store_failure()
        chats.then_nothing_is_stored_after_session_store_failure()

    def test_should_refuse_opening_a_chat_for_a_document(self, chats):
        chats.given_a_signed_in_persons_session_store_fails()
        chats.when_the_person_opens_a_chat_for_a_document_with_failed_session_store()
        chats.then_the_refusal_matches_a_missing_chat_for_session_store_failure()
        chats.then_nothing_is_stored_after_session_store_failure()

    def test_should_refuse_sending_a_line(self, chats):
        chats.given_a_signed_in_persons_session_store_fails()
        chats.when_the_person_sends_a_line_with_failed_session_store()
        chats.then_the_refusal_matches_a_missing_chat_for_session_store_failure()
        chats.then_nothing_is_stored_after_session_store_failure()
