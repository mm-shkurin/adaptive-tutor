from domain.chat.chat import Chat
from domain.chat.exam import draft_choices
from domain.chat.source import Source


async def start_examiner(chat: Chat, model: str, search, answer) -> "Attempt":
    from usecase.chat.send_message import Attempt, ReplyError

    pieces = await search.matching(chat.document_id, chat.document_name or ".")
    sources = Source.cite(pieces)
    if not sources:
        return Attempt(chat.id, ())
    text = await answer(model, "examiner", chat.document_name or ".", sources)
    if text is None:
        return Attempt(chat.id, (), ReplyError.failed())
    choices, supported = draft_choices(sources)
    _updated, lines = chat.record_examiner_question(text, choices, supported)
    return Attempt(chat.id, lines)
