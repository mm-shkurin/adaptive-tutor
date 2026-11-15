import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAQuestionIsAnsweredFromThisPdf(AbstractBackendTest):
    """A question is answered from this PDF with the model, the first page, and at most ten sources.

    Given a signed-in person with an askable chat
    And the PDF has more matching pieces than the reply uses, each with a starting page
    And a neighbour's pieces are in the search store
    When the person sends a question naming a listed model in Professor mode
    Then the tutor line arrives whole
    And the tone is academic
    And the model on the line is the model that was asked
    And the page is the starting page of the first retrieved piece
    And the sources are only pieces of this PDF
    And none of the neighbour's pieces are sources
    And there are at most ten sources
    And each source shows that piece's text and starting page
    And the citation is a page, not a slide
    """

    def test_should_answer_from_this_pdf_with_the_model_and_at_most_ten_sources(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.and_the_pdf_has_more_matching_pieces_than_the_reply_uses_each_with_a_starting_page()
        chats.and_a_neighbours_pieces_are_in_the_search_store()
        chats.when_the_person_sends_a_question_naming_a_listed_model_in_professor_mode()
        chats.then_the_tutor_line_arrives_whole()
        chats.then_the_tone_is_academic()
        chats.then_the_model_on_the_line_is_the_model_that_was_asked()
        chats.then_the_page_is_the_starting_page_of_the_first_retrieved_piece()
        chats.then_the_sources_are_only_pieces_of_this_pdf()
        chats.then_none_of_the_neighbours_pieces_are_sources()
        chats.then_there_are_at_most_ten_sources()
        chats.then_each_source_shows_that_pieces_text_and_starting_page()
        chats.then_the_citation_is_a_page_not_a_slide()
