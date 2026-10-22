import pytest
from uuid import uuid4

from adapters.filestore.file_store import PostgresFileStore


@pytest.mark.skip(reason="RED: FileStore adapter not implemented")
class TestFileStore:
    """FileStore adapter tests.

    Tests the write-through-read-delete flow: put stores content, get retrieves it,
    delete removes it.
    """

    @pytest.mark.asyncio
    async def test_should_store_and_retrieve_content(self, store):
        document_id = uuid4()
        content = b"pdf content"

        await store.put(document_id, content)
        retrieved = await store.get(document_id)

        assert retrieved == content

    @pytest.mark.asyncio
    async def test_should_delete_content(self, store):
        document_id = uuid4()
        content = b"pdf content"

        await store.put(document_id, content)
        await store.delete(document_id)
        retrieved = await store.get(document_id)

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_should_return_none_for_missing_content(self, store):
        document_id = uuid4()

        retrieved = await store.get(document_id)

        assert retrieved is None
