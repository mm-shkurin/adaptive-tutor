import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestACallWithNoSessionIsRefusedLikeAMissingChat(AbstractBackendTest):
    """A call with no session is refused like a missing chat.

    Scenario Outline:
    Given a person who is not signed in
    When the person <asks>
    Then the refusal matches a missing chat
    And nothing is stored
    """

    def test_should_refuse_reading_the_chat_list(self, chats):
        chats.given_a_person_who_is_not_signed_in()
        chats.when_the_person_reads_the_chat_list_without_session()
        chats.then_the_refusal_matches_a_missing_chat()
        chats.then_nothing_is_stored_after_guest_refusal()

    def test_should_refuse_reading_a_chat(self, chats):
        chats.given_a_person_who_is_not_signed_in()
        chats.when_the_person_reads_a_chat_without_session()
        chats.then_the_refusal_matches_a_missing_chat()
        chats.then_nothing_is_stored_after_guest_refusal()

    def test_should_refuse_starting_a_chat(self, chats):
        chats.given_a_person_who_is_not_signed_in()
        chats.when_the_person_starts_a_chat_without_session()
        chats.then_the_refusal_matches_a_missing_chat()
        chats.then_nothing_is_stored_after_guest_refusal()

    def test_should_refuse_opening_a_chat_for_a_document(self, chats):
        chats.given_a_person_who_is_not_signed_in()
        chats.when_the_person_opens_a_chat_for_a_document_without_session()
        chats.then_the_refusal_matches_a_missing_chat()
        chats.then_nothing_is_stored_after_guest_refusal()

    def test_should_refuse_sending_a_line(self, chats):
        chats.given_a_person_who_is_not_signed_in()
        chats.when_the_person_sends_a_line_without_session()
        chats.then_the_refusal_matches_a_missing_chat()
        chats.then_nothing_is_stored_after_guest_refusal()
