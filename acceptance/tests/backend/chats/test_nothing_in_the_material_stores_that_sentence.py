import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestNothingInTheMaterialStoresThatSentence(AbstractBackendTest):
    """Nothing in the material stores that sentence and no sources.

    Given a signed-in person with an askable chat
    And the question matches nothing in this PDF
    When the person sends the question
    Then the tutor says it is not in the material
    And the sources are empty
    And the model did not answer
    """

    def test_should_store_the_not_in_material_sentence(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.and_the_question_matches_nothing_in_this_pdf()
        chats.when_the_person_sends_the_missing_question()
        chats.then_the_tutor_says_it_is_not_in_the_material()
        chats.then_the_sources_are_empty()
        chats.then_the_model_did_not_answer()
