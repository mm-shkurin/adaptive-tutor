import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestSocraticStoresAQuestionAndNoPage(AbstractBackendTest):
    """Socratic stores a question and no page.

    Given a signed-in person with an askable chat
    When the person sends a question in Socratic mode
    Then the tutor stores a question
    And the line has no page
    And the sources are empty
    """

    def test_should_store_a_withheld_question_without_page_or_sources(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_person_sends_a_question_in_socratic_mode()
        chats.then_the_tutor_stores_a_question_without_page_or_sources()
