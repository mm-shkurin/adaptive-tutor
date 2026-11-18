import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAnOmittedModelIsAutoAndAnOmittedModeIsProfessor(AbstractBackendTest):
    """An omitted model is auto and an omitted mode is Professor.

    Given a signed-in person with an askable chat
    When the person sends a line and omits the model and the mode
    Then the tutor line's model is auto
    And the turn is Professor
    """

    def test_should_default_model_and_mode(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_person_sends_a_line_and_omits_the_model_and_the_mode()
        chats.then_the_tutor_lines_model_is_auto()
        chats.then_the_turn_is_professor()
