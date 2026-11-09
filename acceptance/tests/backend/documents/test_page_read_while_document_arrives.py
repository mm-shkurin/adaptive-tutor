import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestPageReadWhileDocumentArrives(AbstractBackendTest):
    """A page read while a document arrives still covers each document once.

    Given a signed-in person who has read the first page
    When a new document sorts into that page and the person reads the next page
    Then each document appears once across the two pages
    And two documents uploaded at the same instant keep the same order on a second read
    """

    def test_should_cover_each_document_once_after_a_new_arrival(self, documents):
        """Given a signed-in person who has read the first page
        When a new document sorts into that page and the person reads the next page
        Then each document appears once across the two pages
        And two documents uploaded at the same instant keep the same order on a second read
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_the_person_owns_more_than_one_page_of_documents()
        documents.when_the_person_has_read_the_first_page()
        documents.when_a_new_document_sorts_into_that_page()
        documents.when_the_person_reads_the_next_page_from_the_first_page_cursor()
        documents.then_each_document_appears_once_across_the_two_pages()
        documents.when_two_documents_are_uploaded_at_the_same_instant()
        documents.when_the_person_reads_the_first_page_again()
        documents.then_two_documents_uploaded_at_the_same_instant_keep_the_same_order()
