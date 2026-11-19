import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAFailureBodyOmitsSecretPieceAndNeighbour(AbstractBackendTest):
    """A failure body and its log omit a secret, the document text, and another person's chat.

    Given a seeded secret, a seeded piece of this PDF, and a seeded line from another person's chat
    And the call fails
    When the person meets that failure
    Then the body is the sanctioned error without leaks
    """

    @pytest.mark.parametrize(
        "call",
        [
            "model call",
            "search",
            "embedding call",
            "reply that misses the latency budget",
        ],
    )
    def test_should_omit_secret_piece_and_neighbour(self, chats, call):
        chats.given_a_seeded_secret_piece_and_neighbour_line()
        chats.and_the_call_fails(call)
        chats.when_the_person_meets_that_failure()
        chats.then_the_body_is_the_sanctioned_error_without_leaks()
