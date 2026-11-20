import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest

STATES = ("waiting", "indexing", "failed")


@pytest.mark.frontend
class TestDocumentThatIsNotReadyCannotBeChosen(AbstractUiTest):
    """UI Test Scenario 0.3: A document that is not ready cannot be chosen

    Scenario Outline:
    Given a signed-in person with a ready PDF
    And a document of theirs that is <state>
    When the person opens the chat
    Then that document is not a choice for a new chat or a switch
    And no chat is bound to it
    """

    @pytest.mark.parametrize("state", STATES)
    def test_should_omit_not_ready_document_from_choices(
        self, signed_in_browser, chat_screen, state
    ):
        signed_in_browser.given_a_signed_in_person_with_a_ready_pdf_and_a_document_in_state(
            state
        )
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_opens_the_document_picker()
        chat_screen.then_document_is_a_choice(signed_in_browser.ready_name)
        chat_screen.then_document_is_not_a_choice(signed_in_browser.not_ready_name)
        chat_screen.when_the_person_starts_a_new_chat()
        signed_in_browser.then_no_chat_is_bound_to_document_named(
            signed_in_browser.not_ready_name
        )
