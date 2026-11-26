from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from adapters.persistence.tables import ChatAttemptRow, ChatLineRow, ChatRow
from usecase.chat.errors import ChatNotFound
from usecase.chat.send_message import Attempt


async def append_attempt(
    session,
    owner_id: UUID,
    chat_id: UUID,
    attempt_key: str,
    attempt: Attempt,
    created_at: datetime,
) -> None:
    row = await session.scalar(
        select(ChatRow)
        .where(ChatRow.id == chat_id, ChatRow.owner_id == owner_id)
        .options(selectinload(ChatRow.lines))
        .with_for_update()
    )
    if row is None:
        raise ChatNotFound()
    existing = await session.get(ChatAttemptRow, {"chat_id": chat_id, "attempt_key": attempt_key})
    if existing is not None:
        return
    if attempt.persist:
        start = len(row.lines)
        row.lines.extend(
            ChatLineRow.from_line(chat_id, start + offset, line, created_at)
            for offset, line in enumerate(attempt.lines)
        )
    error = attempt.error
    session.add(
        ChatAttemptRow(
            chat_id=chat_id,
            attempt_key=attempt_key,
            line_ids=[str(line.id) for line in attempt.lines],
            error_code=None if error is None else error.code,
            error_message=None if error is None else error.message,
        )
    )
