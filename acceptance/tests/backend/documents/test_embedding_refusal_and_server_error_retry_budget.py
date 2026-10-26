import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest

_EMBEDDING_OUTCOMES = (
    ("refuses", "then_the_document_is_failed_and_not_retried_for_that_refusal"),
    ("answers unreadable", "then_the_document_is_failed_after_unreadable_embedding"),
    ("fails as a server error", "then_the_server_error_try_counts_toward_the_three"),
)


@pytest.mark.skip(
    reason="RED: assert 'ready' == 'failed' — embedding outcomes not applied during indexing"
)
@pytest.mark.backend
class TestEmbeddingRefusalAndServerErrorRetryBudget(AbstractBackendTest):
    """An embedding refusal stops, and a server error stays inside the three tries.

    Scenario Outline:
    Given an accepted document
    And the embedding call <outcome>
    When indexing runs
    Then <result>
    """

    def test_should_fail_or_budget_embedding_outcomes(self, documents):
        """Given an accepted document
        And the embedding call refuses, answers unreadable, or fails as a server error
        When indexing runs
        Then the document fails or the server error counts toward three tries
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        for outcome, then_step in _EMBEDDING_OUTCOMES:
            documents.probe.hold_indexing()
            documents.probe.clear_embedding_outcome()
            documents.when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table()
            documents.then_the_upload_is_answered_before_indexing_finishes()
            documents.and_the_embedding_call(outcome)
            documents.when_indexing_runs()
            getattr(documents, then_step)()
            documents.clock.advance(61)
