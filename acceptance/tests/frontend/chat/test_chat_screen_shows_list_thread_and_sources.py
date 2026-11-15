import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestChatScreenShowsListThreadAndSources(AbstractUiTest):
    """UI Test Scenario 1.1: The chat screen shows the list, the thread, and the sources

    Given a signed-in person with a chat that has a person line and a tutor line
    When the person opens that chat
    Then the list row shows the document name and the last person line
    And the thread shows the person line, the tutor line, the model, and the page
    And the sources show the page and the piece text
    And the citation is a page, not a slide
    """

    def test_should_show_list_thread_and_sources(self, signed_in_browser, chat_screen):
        """UI Test Scenario 1.1: The chat screen shows the list, the thread, and the sources

        Given a signed-in person with a chat that has a person line and a tutor line
        When the person opens that chat
        Then the list row shows the document name and the last person line
        And the thread shows the person line, the tutor line, the model, and the page
        And the sources show the page and the piece text
        And the citation is a page, not a slide
        """
        signed_in_browser.given_a_signed_in_person_with_a_chat_that_has_a_person_line_and_a_tutor_line()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.then_the_list_row_shows_the_document_name_and_the_last_person_line(
            signed_in_browser.ready_document.body["name"],
            signed_in_browser.person_line,
        )
        chat_screen.then_the_thread_shows_the_person_line_the_tutor_line_the_model_and_the_page(
            signed_in_browser.person_line,
            signed_in_browser.tutor_line,
            signed_in_browser.model,
            signed_in_browser.page,
        )
        chat_screen.then_the_sources_show_the_page_and_the_piece_text(
            signed_in_browser.page,
            signed_in_browser.source_text,
        )
        chat_screen.then_the_citation_is_a_page_not_a_slide()
