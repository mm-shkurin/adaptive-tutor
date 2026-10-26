import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestFailureEchoesNoSecretFileTextStackOrPath(AbstractBackendTest):
    """A failure echoes no secret, file text, stack, or path.

    Given a known secret and a phrase that appears only in the PDF
    When an upload is refused, indexing fails, the virus check rejects the file, or the upload count cannot be read
    Then the answer and the log do not contain the secret
    And the answer and the log do not contain that phrase
    And the answer and the log do not contain a stack, a file path, or an internal name
    """

    def test_should_keep_failure_answers_and_logs_free_of_secrets_and_internals(self, documents):
        """Given a known secret and a phrase that appears only in the PDF
        When an upload is refused, indexing fails, the virus check rejects the file, or the upload count cannot be read
        Then the answer and the log do not contain the secret
        And the answer and the log do not contain that phrase
        And the answer and the log do not contain a stack, a file path, or an internal name
        """
        documents.given_a_known_secret_and_a_phrase_that_appears_only_in_the_pdf()
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.when_an_upload_is_refused_for_the_pdf_with_the_phrase()
        documents.then_the_answer_and_the_log_do_not_contain_the_secret_the_phrase_a_stack_a_file_path_or_an_internal_name()
        documents.when_indexing_fails_for_the_pdf_with_the_phrase()
        documents.then_the_answer_and_the_log_do_not_contain_the_secret_the_phrase_a_stack_a_file_path_or_an_internal_name()
        documents.when_the_virus_check_rejects_the_pdf_with_the_phrase()
        documents.then_the_answer_and_the_log_do_not_contain_the_secret_the_phrase_a_stack_a_file_path_or_an_internal_name()
        documents.when_the_upload_count_cannot_be_read_for_the_pdf_with_the_phrase()
        documents.then_the_answer_and_the_log_do_not_contain_the_secret_the_phrase_a_stack_a_file_path_or_an_internal_name()
