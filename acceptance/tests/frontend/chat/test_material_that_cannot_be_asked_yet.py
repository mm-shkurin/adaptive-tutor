import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestMaterialThatCannotBeAskedYet(AbstractUiTest):
    """UI Test Scenario 0.4: The material that cannot be asked yet shows the sentence and send adds nothing

    Given a signed-in person whose chat cannot be asked yet
    When the person opens that chat
    Then the chat says the material cannot be asked yet
    And sending adds no line
    """

    def test_should_show_notice_and_refuse_send(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_whose_chat_cannot_be_asked_yet()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.then_the_material_cannot_be_asked_yet()
        chat_screen.when_the_person_tries_to_send_while_not_askable()
        chat_screen.then_sending_added_no_line()
