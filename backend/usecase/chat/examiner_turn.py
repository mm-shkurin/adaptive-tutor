from domain.chat.chat import Chat, ChoiceRequired
from domain.chat.learning import LearningMode
from usecase.chat.examiner_grade import grade_examiner
from usecase.chat.examiner_start import start_examiner
from usecase.chat.outgoing import Outgoing


async def examiner_or_choice(chat: Chat, outgoing: Outgoing, model: str, search, answer):
    from usecase.chat.send_message import Attempt

    if outgoing.has_choice:
        return await grade_examiner(chat, outgoing.choice_id, model, search, answer)
    mode = LearningMode.parse(outgoing.mode, outgoing.mode_present)
    if chat.open_examiner_question() is not None:
        if mode.value == "examiner" and not isinstance(outgoing.text, str):
            return Attempt(chat.id, ())
        raise ChoiceRequired()
    if mode.value == "examiner" and not isinstance(outgoing.text, str):
        if chat.examiner_series_stopped():
            return Attempt(chat.id, ())
        return await start_examiner(chat, model, search, answer)
    return None
