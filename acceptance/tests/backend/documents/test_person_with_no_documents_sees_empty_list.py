import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestPersonWithNoDocumentsSeesEmptyList(AbstractBackendTest):
    """A person with no documents sees an empty list.

    Given a signed-in person with no documents
    When the person reads their documents
    Then the list is empty
    """

    def test_should_show_an_empty_list(self, documents):
        """Given a signed-in person with no documents
        When the person reads their documents
        Then the list is empty
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.when_the_person_lists_documents()
        documents.then_the_list_is_empty()
