import pytest

from statements.document_statements import MAX_BYTES, MIN_BYTES
from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestFileAtSizeEdgeStoredAsByteCount(AbstractBackendTest):
    """A file at either size edge is stored as that byte count.

    Scenario Outline:
    Given a signed-in person
    When the person submits a PDF of <size>
    Then the document is accepted
    And the stored size is <size>
    And the size the person reads back is <size>

    Examples:
      | size |
      | the minimum |
      | the maximum |
    """

    def test_should_store_minimum_and_maximum_byte_counts(self, documents):
        """Given a signed-in person
        When the person submits a PDF of the minimum or maximum size
        Then the document is accepted at that byte count on upload and read-back
        """
        documents.probe.hold_indexing()
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        for size_bytes in (MIN_BYTES, MAX_BYTES):
            documents.when_the_person_submits_a_pdf_of(size_bytes)
            documents.then_the_document_is_accepted_at_that_size()
            documents.then_the_stored_size_is_that_byte_count()
            documents.when_the_person_reads_the_document()
            documents.then_the_size_the_person_reads_back_is_that_byte_count()
            if size_bytes == MIN_BYTES:
                documents.clock.advance(61)
