import pytest

from statements.signed_in_browser_statements import READY_NAME
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestCardShowsDocumentTopicCountAndScore(AbstractUiTest):
    """UI 1.2: A card shows the document, the topic, the count, and only the last completed score."""

    def test_should_show_completed_score_not_open_attempt(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_a_finished_quiz_started_again()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.then_card_shows_document_topic_count_and_completed_score(
            READY_NAME,
            "cells",
            "3 вопроса",
            "Прошлый результат: 3 / 3",
        )
