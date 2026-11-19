import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestRepeatedFailedSendsReturnTheStoreConnectionsToBaseline(AbstractBackendTest):
    """Repeated failed sends return the store connections to baseline.

    Given a signed-in person with an askable chat
    When several sends fail because the chat store or the search store is unavailable
    Then the open store connections return to the baseline
    And a further send can still be stored once the store is back
    """

    def test_should_return_store_connections_to_baseline(self, chats):
        """Given a signed-in person with an askable chat
        When several sends fail because the chat store or the search store is unavailable
        Then the open store connections return to the baseline
        And a further send can still be stored once the store is back
        """
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.given_the_chat_store_connection_baselines()
        chats.when_several_sends_fail_because_the_chat_store_or_the_search_store_is_unavailable()
        chats.then_the_open_store_connections_return_to_the_baseline()
        chats.then_a_further_send_can_still_be_stored_once_the_store_is_back()
