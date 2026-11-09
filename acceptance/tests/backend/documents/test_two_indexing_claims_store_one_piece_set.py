import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTwoIndexingClaimsStoreOnePieceSet(AbstractBackendTest):
    """Two indexing claims of one document store one set of pieces.

    Given an accepted document
    When two indexing claims pass the status check together
    Then one claim proceeds
    And one set of pieces is stored
    """

    def test_should_store_one_piece_set_when_two_claims_race(self, documents):
        """Given an accepted document
        When two indexing claims pass the status check together
        Then one claim proceeds
        And one set of pieces is stored
        """
        documents.given_an_accepted_document()
        documents.when_two_indexing_claims_pass_the_status_check_together()
        documents.then_one_claim_proceeds()
        documents.then_one_set_of_pieces_is_stored()
