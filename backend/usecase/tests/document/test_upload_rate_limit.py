import pytest


class TestSixthUploadInTheMinuteIsRefused:
    """A sixth upload in the minute is refused and the five stay.

    Given a signed-in person who has five accepted uploads in the current minute
    When the person submits a sixth PDF
    Then the upload is refused
    And the five documents stay
    """

    @pytest.mark.asyncio
    async def test_should_refuse_the_sixth_and_keep_the_five(self, documents):
        await documents.given_a_signed_in_person()
        await documents.given_five_accepted_uploads_in_the_current_minute()
        await documents.when_the_person_submits_a_sixth_pdf()
        await documents.then_the_upload_is_refused_as_rate_limited()
        await documents.then_the_five_documents_stay()


class TestTwoUploadsOnLastSlotAcceptOnlyOne:
    """Two uploads that arrive together on the last free slot accept only one.

    Given a signed-in person with four accepted uploads in the current minute
    When two uploads pass the count check together
    Then one of them is accepted
    And the other is refused
    And five documents exist
    """

    @pytest.mark.asyncio
    async def test_should_accept_only_one_of_two_on_the_last_slot(self, documents):
        await documents.given_a_signed_in_person()
        await documents.given_four_accepted_uploads_in_the_current_minute()
        await documents.when_two_uploads_pass_the_count_check_together()
        await documents.then_one_of_them_is_accepted_and_the_other_is_refused()
        await documents.then_five_documents_exist()


class TestUploadAtStartOfNextMinuteIsAccepted:
    """An upload at the start of the next minute is accepted.

    Given a signed-in person who has five accepted uploads in this minute
    When the clock is just short of the next minute
    Then a sixth upload is still refused
    When the minute window has just opened
    Then the next upload is accepted
    And the five from the previous minute stay
    """

    @pytest.mark.asyncio
    async def test_should_accept_again_after_the_minute_opens(self, documents):
        await documents.given_a_signed_in_person()
        await documents.given_five_accepted_uploads_in_the_current_minute()
        await documents.when_the_clock_is_just_short_of_the_next_minute()
        await documents.then_a_sixth_upload_is_still_refused()
        await documents.when_the_minute_window_has_just_opened()
        await documents.then_the_next_upload_is_accepted()
        await documents.then_the_five_from_the_previous_minute_stay()


class TestUnreadableUploadCountRefusesTheUpload:
    """An unreadable upload count refuses the upload.

    Given a signed-in person
    And the upload count cannot be read
    When the person submits a valid PDF
    Then the upload is refused
    And no document is added
    """

    @pytest.mark.asyncio
    async def test_should_refuse_when_the_count_cannot_be_read(self, documents):
        await documents.given_a_signed_in_person()
        await documents.given_the_upload_count_cannot_be_read()
        await documents.when_the_person_submits_a_valid_pdf_under_rate_check()
        await documents.then_the_upload_is_refused_as_rate_unavailable()
        await documents.then_no_document_is_added()
