import pytest

_EMBEDDING_OUTCOMES = (
    ("refuses", "then_the_document_is_failed_and_not_retried_for_that_refusal"),
    ("answers unreadable", "then_the_document_is_failed_after_unreadable_embedding"),
    ("fails as a server error", "then_the_server_error_try_counts_toward_the_three"),
)


class TestEmbeddingRefusalAndServerErrorRetryBudget:
    """An embedding refusal stops, and a server error stays inside the three tries.

    Scenario Outline:
    Given an accepted document
    And the embedding call <outcome>
    When indexing runs
    Then <result>
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize("outcome,then_step", _EMBEDDING_OUTCOMES)
    async def test_should_fail_or_budget_embedding_outcomes(self, documents, outcome, then_step):
        await documents.given_an_accepted_document()
        await documents.and_the_embedding_call(outcome)
        await documents.when_indexing_runs_for_embedding()
        await getattr(documents, then_step)()
