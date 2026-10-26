import pytest


class TestSameSubmissionStoredTwiceIsOneDocument:
    """The same submission stored twice is one document.

    Given a signed-in person
    When the same submission is delivered twice
    Then one document exists for that submission
    And the second delivery does not add a second document
    And the second delivery does not count as another upload in the minute
    """

    @pytest.mark.asyncio
    async def test_should_keep_one_document_and_skip_the_rate_slot(self, documents):
        await documents.given_a_signed_in_person()
        await documents.when_the_same_submission_is_delivered_twice()
        await documents.then_one_document_exists_for_that_submission()
        await documents.then_the_second_delivery_does_not_add_a_second_document()
        await documents.then_the_second_delivery_does_not_count_as_another_upload()


class TestTwoOverlappingCopiesStoreOneDocument:
    """Two overlapping copies of one submission store one document.

    Given two deliveries of one submission pass the existence check together
    When both deliveries complete
    Then one document exists for that submission
    """

    @pytest.mark.asyncio
    async def test_should_store_one_document_when_copies_overlap(self, documents):
        await documents.given_a_signed_in_person()
        await documents.when_two_overlapping_copies_of_one_submission_complete()
        await documents.then_one_document_exists_after_overlapping_copies()


class TestUploadingSamePdfAgainCreatesAnotherDocument:
    """Uploading the same PDF again creates another document.

    Given a signed-in person who already uploaded a PDF
    When the person uploads that PDF again as a new submission
    Then two documents exist
    And the earlier document is unchanged
    """

    @pytest.mark.asyncio
    async def test_should_create_another_document_for_a_new_submission(self, documents):
        await documents.given_a_signed_in_person()
        await documents.given_the_person_already_uploaded_a_pdf()
        await documents.when_the_person_uploads_that_pdf_again_as_a_new_submission()
        await documents.then_two_documents_exist()
        await documents.then_the_earlier_document_is_unchanged()
