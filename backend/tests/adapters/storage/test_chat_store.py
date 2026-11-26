from datetime import datetime, timezone
from uuid import uuid4

import pytest

from adapters.storage.chat_store import PostgresChatStore
from domain.chat.chat import Chat
from domain.chat.source import Source
from domain.document.document import Document


@pytest.mark.asyncio
async def test_should_list_a_chat_bound_to_its_document(sessions, intake):
    owner_id = uuid4()
    document = Document.accepted("older.pdf", 2048).ready(1, 1)
    await intake.store(owner_id, document, b"pdf", str(uuid4()))
    chat = Chat.bound_to(document)
    created_at = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)

    await PostgresChatStore(sessions).add(owner_id, chat, created_at)
    listed = await PostgresChatStore(sessions).list_for(owner_id)

    assert listed == (Chat.stored(chat.id, document.id, "older.pdf"),)
    assert listed[0].preview() is None
    assert listed[0].lines == ()


@pytest.mark.asyncio
async def test_should_keep_the_reply_lines_on_the_chat(sessions, intake):
    owner_id = uuid4()
    document = Document.accepted("lecture.pdf", 2048).ready(2, 2)
    await intake.store(owner_id, document, b"pdf", str(uuid4()))
    chat = Chat.bound_to(document)
    created_at = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)
    store = PostgresChatStore(sessions)
    await store.add(owner_id, chat, created_at)
    updated, _lines = chat.record_grounded(
        "Why?",
        "qwen/qwen3-32b",
        "professor",
        (Source(page=4, text="piece-0"),),
        "Because the lecture says so.",
    )

    await store.save(owner_id, updated)
    listed = await store.list_for(owner_id)

    assert listed[0].preview() == "Why?"
    assert listed[0].lines[1].text == "Because the lecture says so."
    assert listed[0].lines[1].model == "qwen/qwen3-32b"
    assert listed[0].lines[1].mode == "professor"
    assert listed[0].lines[1].kind == "reply"
    assert listed[0].lines[1].page == 4
    assert listed[0].lines[1].sources == (Source(page=4, text="piece-0"),)


@pytest.mark.asyncio
async def test_should_return_person_send_times_for_progress(sessions, intake):
    owner_id = uuid4()
    document = Document.accepted("study.pdf", 2048).ready(1, 1)
    await intake.store(owner_id, document, b"pdf", str(uuid4()))
    chat = Chat.bound_to(document)
    created_at = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)
    store = PostgresChatStore(sessions)
    await store.add(owner_id, chat, created_at)
    updated, _lines = chat.record_grounded(
        "hello",
        "qwen/qwen3-32b",
        "professor",
        (Source(page=1, text="piece-0"),),
        "reply",
    )
    await store.save(owner_id, updated)
    sends = await store.person_send_times(owner_id)
    assert len(sends) == 1
    assert isinstance(sends[0], datetime)
