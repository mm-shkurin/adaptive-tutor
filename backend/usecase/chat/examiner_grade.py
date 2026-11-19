from domain.chat.chat import Chat, ChoiceRequired, ChoiceUnknown, EXAMINER_SERIES
from domain.chat.source import Source
from usecase.chat.examiner_start import start_examiner


async def grade_examiner(
    chat: Chat, choice_id: object, model: str, search, answer
) -> "Attempt":
    from usecase.chat.send_message import Attempt

    if chat.open_examiner_question() is None:
        previous = chat.last_examiner_grade()
        if previous is not None:
            return Attempt(chat.id, (previous,), persist=False)
        raise ChoiceUnknown()
    if not isinstance(choice_id, str):
        raise ChoiceRequired()
    chosen = chat.require_examiner_choice(choice_id)
    pieces = await search.matching(chat.document_id, chat.document_name or ".")
    sources = Source.cite(pieces)
    page = sources[0].page if sources else None
    updated, grade_lines = chat.record_examiner_grade(chosen, page)
    if updated.examiner_grade_count() >= EXAMINER_SERIES:
        return Attempt(chat.id, grade_lines)
    follow = await start_examiner(updated, model, search, answer)
    return Attempt(chat.id, grade_lines + follow.lines)
