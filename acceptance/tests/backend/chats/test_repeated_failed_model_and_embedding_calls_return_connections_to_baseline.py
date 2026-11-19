import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestRepeatedFailedModelAndEmbeddingCallsReturnConnectionsToBaseline(AbstractBackendTest):
    """Repeated failed model and embedding calls return connections to baseline.

    Given a signed-in person with an askable chat
    When several model calls and embedding calls fail
    Then the open connections return to the baseline
    """

    def test_should_return_connections_to_baseline(self, chats):
        """Given a signed-in person with an askable chat
        When several model calls and embedding calls fail
        Then the open connections return to the baseline
        """
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.given_the_chat_store_connection_baselines()
        chats.when_several_model_calls_and_embedding_calls_fail()
        chats.then_the_open_connections_return_to_the_baseline()
