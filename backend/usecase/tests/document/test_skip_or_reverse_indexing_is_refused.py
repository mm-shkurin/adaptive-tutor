import pytest

from domain.document.document import Document, InvalidStatusTransition

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

LEGAL_MOVES = [
    ("waiting", "indexing", "indexing"),
    ("indexing", "ready", "ready"),
    ("indexing", "failed", "failed"),
]


def _document(status: str) -> Document:
    accepted = Document.accepted("lecture.pdf", 2_000_000)
    if status == "waiting":
        return accepted
    if status == "indexing":
        return accepted.indexing()
    if status == "ready":
        return accepted.indexing().ready(1, 2)
    return accepted.indexing().failed("named part")


class TestSkipOrReverseIndexingIsRefused:
    """A step that skips or reverses indexing is refused.

    Given a document that is <from>
    When the document is moved <toward>
    Then the move is refused
    And the document stays <from>
    """

    @pytest.mark.parametrize(("frm", "toward"), ILLEGAL_MOVES)
    def test_should_refuse_a_skip_or_reverse(self, frm, toward):
        document = _document(frm)
        with pytest.raises(InvalidStatusTransition):
            document.transition(toward)
        assert document.status == frm

    @pytest.mark.parametrize(("frm", "toward", "expected"), LEGAL_MOVES)
    def test_should_allow_a_forward_step(self, frm, toward, expected):
        assert _document(frm).transition(toward).status == expected
