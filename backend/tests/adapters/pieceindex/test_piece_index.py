from uuid import uuid4

import pytest

from adapters.pieceindex.piece_index import PostgresPieceIndex


class TestPieceIndex:
    """PieceIndex adapter tests.

    Tests replace/read of pieces and extracted text for one document.
    """

    @pytest.mark.asyncio
    async def test_should_replace_and_read_pieces(self, pieces: PostgresPieceIndex):
        document_id = uuid4()
        stored = ("first piece", "second piece")

        await pieces.replace(document_id, stored, "full extracted")
        retrieved = await pieces.pieces(document_id)

        assert retrieved == stored

    @pytest.mark.asyncio
    async def test_should_read_extracted_text(self, pieces: PostgresPieceIndex):
        document_id = uuid4()

        await pieces.replace(document_id, ("only",), "full extracted")
        retrieved = await pieces.extracted(document_id)

        assert retrieved == "full extracted"

    @pytest.mark.asyncio
    async def test_should_replace_over_previous_pieces(self, pieces: PostgresPieceIndex):
        document_id = uuid4()

        await pieces.replace(document_id, ("old", "pieces"), "old extracted")
        await pieces.replace(document_id, ("new",), "new extracted")

        assert await pieces.pieces(document_id) == ("new",)
        assert await pieces.extracted(document_id) == "new extracted"
