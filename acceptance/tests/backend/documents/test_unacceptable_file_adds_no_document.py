import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestUnacceptableFileAddsNoDocument(AbstractBackendTest):
    """An unacceptable file adds no document.

    Scenario Outline:
    Given a signed-in person with one document
    When the person <submits>
    Then the upload is refused
    And the list is unchanged
    """

    def test_should_refuse_no_file(self, documents):
        """Given a signed-in person with one document
        When the person submits no file
        Then the upload is refused
        And the list is unchanged
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.when_the_person_submits_no_file()
        documents.then_the_upload_is_refused("file_missing")
        documents.then_the_list_is_unchanged()

    def test_should_refuse_a_file_that_is_not_a_pdf(self, documents):
        """Given a signed-in person with one document
        When the person submits a file that is not a PDF
        Then the upload is refused
        And the list is unchanged
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.when_the_person_submits_a_file_that_is_not_a_pdf()
        documents.then_the_upload_is_refused("invalid_pdf")
        documents.then_the_list_is_unchanged()

    def test_should_refuse_a_pdf_with_no_text(self, documents):
        """Given a signed-in person with one document
        When the person submits a PDF with no text
        Then the upload is refused
        And the list is unchanged
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.when_the_person_submits_a_pdf_with_no_text()
        documents.then_the_upload_is_refused("empty_pdf")
        documents.then_the_list_is_unchanged()

    def test_should_refuse_a_pdf_one_byte_under_the_minimum(self, documents):
        """Given a signed-in person with one document
        When the person submits a PDF one byte under the minimum
        Then the upload is refused
        And the list is unchanged
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.when_the_person_submits_a_pdf_one_byte_under_the_minimum()
        documents.then_the_upload_is_refused("file_too_small")
        documents.then_the_list_is_unchanged()

    def test_should_refuse_a_pdf_one_byte_over_the_maximum(self, documents):
        """Given a signed-in person with one document
        When the person submits a PDF one byte over the maximum
        Then the upload is refused
        And the list is unchanged
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.when_the_person_submits_a_pdf_one_byte_over_the_maximum()
        documents.then_the_upload_is_refused("file_too_large")
        documents.then_the_list_is_unchanged()

    def test_should_refuse_an_encrypted_pdf(self, documents):
        """Given a signed-in person with one document
        When the person submits an encrypted PDF
        Then the upload is refused
        And the list is unchanged
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.when_the_person_submits_an_encrypted_pdf()
        documents.then_the_upload_is_refused("encrypted_pdf")
        documents.then_the_list_is_unchanged()

    def test_should_refuse_a_pdf_with_no_file_name(self, documents):
        """Given a signed-in person with one document
        When the person submits a PDF with no file name
        Then the upload is refused
        And the list is unchanged
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.when_the_person_submits_a_pdf_with_no_file_name()
        documents.then_the_upload_is_refused("name_missing")
        documents.then_the_list_is_unchanged()
