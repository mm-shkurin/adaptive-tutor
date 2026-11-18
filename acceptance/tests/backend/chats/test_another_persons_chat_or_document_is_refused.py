import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAnotherPersonsChatOrDocumentIsRefused(AbstractBackendTest):
    """Another person's chat or document is refused like a missing chat.

    Scenario Outline:
    Given a signed-in person
    And a neighbour who owns <target>
    When the person <asks>
    Then the refusal matches a missing chat
    And nothing of the neighbour's is stored or returned
    """

    def test_should_refuse_reading_the_neighbours_chat(self, chats):
        chats.given_a_signed_in_person_and_a_neighbour_who_owns_a_chat()
        chats.when_the_person_reads_the_neighbours_chat()
        chats.then_the_idor_refusal_matches_a_missing_chat()
        chats.then_nothing_of_the_neighbours_is_stored_or_returned()

    def test_should_refuse_sending_to_the_neighbours_chat(self, chats):
        chats.given_a_signed_in_person_and_a_neighbour_who_owns_a_chat()
        chats.when_the_person_sends_a_line_to_the_neighbours_chat()
        chats.then_the_idor_refusal_matches_a_missing_chat()
        chats.then_nothing_of_the_neighbours_is_stored_or_returned()

    def test_should_refuse_starting_a_chat_on_the_neighbours_pdf(self, chats):
        chats.given_a_signed_in_person_and_a_neighbour_who_owns_a_ready_pdf()
        chats.when_the_person_starts_a_chat_on_the_neighbours_pdf()
        chats.then_the_idor_refusal_matches_a_missing_chat()
        chats.then_nothing_of_the_neighbours_is_stored_or_returned()

    def test_should_refuse_opening_a_chat_for_the_neighbours_pdf(self, chats):
        chats.given_a_signed_in_person_and_a_neighbour_who_owns_a_ready_pdf()
        chats.when_the_person_opens_a_chat_for_the_neighbours_pdf()
        chats.then_the_idor_refusal_matches_a_missing_chat()
        chats.then_nothing_of_the_neighbours_is_stored_or_returned()
