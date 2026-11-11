import pytest
from datetime import datetime, timezone
from uuid import uuid4

from adapters.filestore.file_store import PostgresFileStore
from adapters.persistence.tables import DocumentRow


def _row(document_id):
    return DocumentRow(
        id=document_id,
        owner_id=uuid4(),
        idempotency_key=str(uuid4()),
        name="test.pdf",
        size_bytes=1024,
        page_count=None,
        piece_count=None,
        status="waiting",
        error=None,
        body=b"",
        created_at=datetime.now(timezone.utc),
    )


class TestFileStore:
    """FileStore adapter tests.

    Tests the write-through-read-delete flow: put stores content, get retrieves it,
    delete removes it.
    """

    @pytest.mark.asyncio
    async def test_should_store_and_retrieve_content(self, sessions):
        document_id = uuid4()
        content = b"pdf content"
        store = PostgresFileStore(sessions)

        async with sessions() as session:
            async with session.begin():
                session.add(_row(document_id))

        await store.put(document_id, content)
        retrieved = await store.get(document_id)

        assert retrieved == content

    @pytest.mark.asyncio
    async def test_should_delete_content(self, sessions):
        document_id = uuid4()
        content = b"pdf content"
        store = PostgresFileStore(sessions)

        async with sessions() as session:
            async with session.begin():
                session.add(_row(document_id))

        await store.put(document_id, content)
        await store.delete(document_id)
        retrieved = await store.get(document_id)

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_should_return_none_for_missing_content(self, sessions):
        document_id = uuid4()
        store = PostgresFileStore(sessions)

        retrieved = await store.get(document_id)

        assert retrieved is None
