import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest

ILLEGAL_MOVES = [
    ("waiting", "ready"),
    ("waiting", "failed"),
    ("indexing", "waiting"),
    ("ready", "waiting"),
    ("ready", "failed"),
    ("ready", "indexing"),
    ("failed", "waiting"),
    ("failed", "ready"),
    ("failed", "indexing"),
]


@pytest.mark.backend
class TestSkipOrReverseIndexingIsRefused(AbstractBackendTest):
    """A step that skips or reverses indexing is refused.

    Scenario Outline:
    Given a document that is <from>
    When the document is moved <toward>
    Then the move is refused
    And the document stays <from>
    And its pieces, its search entries, and its file are untouched
    """

    @pytest.mark.parametrize(("frm", "toward"), ILLEGAL_MOVES)
    def test_should_refuse_a_skip_or_reverse(self, documents, frm, toward):
        """Given a document that is <from>
        When the document is moved <toward>
        Then the move is refused
        And the document stays <from>
        And its pieces, its search entries, and its file are untouched
        """
        documents.given_a_document_that_is(frm)
        documents.when_the_document_is_moved_toward(toward)
        documents.then_the_move_is_refused()
        documents.then_the_document_stays(frm)
        documents.then_its_pieces_its_search_entries_and_its_file_are_untouched()
