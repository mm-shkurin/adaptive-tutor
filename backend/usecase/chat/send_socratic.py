from domain.chat.chat import Chat
from domain.chat.line import Line
from domain.chat.source import Source


async def socratic(send, chat: Chat, question: str, model: str, started):
    from usecase.chat.send_message import Attempt, ReplyError

    pieces = await send._match(chat, question)
    if pieces is None:
        _updated, lines = chat.record_failed(question)
        return Attempt(chat.id, lines, ReplyError.failed())
    sources = Source.cite(pieces)
    if not sources:
        _updated, lines = chat.record_missing(question, "socratic")
        return Attempt(chat.id, lines)
    text = await send._answer(model, "socratic", question, sources, started)
    if text is None:
        _updated, lines = chat.record_failed(question)
        return Attempt(chat.id, lines, ReplyError.failed())
    _updated, lines = chat.record_withheld(question, "socratic", text)
    return Attempt(chat.id, lines)


async def release(
    send, chat: Chat, try_text: str | None, model: str, mode: str, started, prompt=None
):
    from usecase.chat.send_message import Attempt, ReplyError

    ask = prompt if prompt is not None else (try_text or "")
    pieces = await send._match(chat, ask)
    if pieces is None:
        if try_text is None:
            return Attempt(chat.id, (), ReplyError.failed())
        _updated, lines = chat.record_failed(try_text)
        return Attempt(chat.id, lines, ReplyError.failed())
    sources = Source.cite(pieces)
    if not sources:
        if try_text is None:
            return Attempt(chat.id, (Line.missing(mode),))
        _updated, lines = chat.record_missing(try_text, mode)
        return Attempt(chat.id, lines)
    text = await send._answer(model, mode, ask, sources, started)
    if text is None:
        if try_text is None:
            return Attempt(chat.id, (), ReplyError.failed())
        _updated, lines = chat.record_failed(try_text)
        return Attempt(chat.id, lines, ReplyError.failed())
    _updated, lines = chat.record_release(try_text, model, mode, sources, text)
    return Attempt(chat.id, lines)
