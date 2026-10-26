import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestListIsPersonsNewestPage(AbstractBackendTest):
    """The list is this person's newest page.

    Given a signed-in person with more documents than one page
    And a neighbour with a document of their own
    When the person reads the first page
    Then the page holds at most fifty documents
    And the newest document is first
    And a later page holds the rest
    And the neighbour's document is absent
    """

    def test_should_return_newest_first_across_pages_without_neighbour_docs(self, documents):
        """Given a signed-in person with more documents than one page
        And a neighbour with a document of their own
        When the person reads the first page
        Then the page holds at most fifty documents
        And the newest document is first
        And a later page holds the rest
        And the neighbour's document is absent
        """
        documents.given_a_signed_in_person_with_more_documents_than_one_page()
        documents.given_a_neighbour_with_a_document_of_their_own()
        documents.when_the_person_reads_the_first_page()
        documents.then_the_page_holds_at_most_fifty_documents()
        documents.then_the_newest_document_is_first()
        documents.when_the_person_reads_the_next_page()
        documents.then_a_later_page_holds_the_rest()
        documents.then_the_neighbours_document_is_absent()
