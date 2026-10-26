import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestMissingNeighbourAndGuestOpenLookTheSame(AbstractBackendTest):
    """A missing document, a neighbour's document, and a guest's open look the same.

    Given a signed-in person and a neighbour with a document
    When each of these opens a document: the neighbour's id, an id that does not exist, and a guest opening the person's id
    Then each refusal is the same status and the same body
    And none of them includes the document's name or text
    """

    def test_should_refuse_each_open_with_the_same_missing_document_answer(self, documents):
        """Given a signed-in person and a neighbour with a document
        When each of these opens a document: the neighbour's id, an id that does not exist, and a guest opening the person's id
        Then each refusal is the same status and the same body
        And none of them includes the document's name or text
        """
        documents.given_a_signed_in_person_and_a_neighbour_with_a_document()
        documents.when_the_person_opens_the_neighbours_document()
        documents.when_the_person_opens_a_document_that_does_not_exist()
        documents.when_a_guest_opens_the_persons_document()
        documents.then_each_refusal_is_the_same_status_and_the_same_body()
        documents.then_none_of_them_includes_the_documents_name_or_text()
