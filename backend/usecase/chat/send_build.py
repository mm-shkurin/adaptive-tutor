from domain.chat.learning import ListedModel
from usecase.chat.outgoing import Outgoing
from usecase.chat.send_snapshot import SendSnapshot


async def build_attempt(send, owner_id, chat_id, outgoing: Outgoing, attempt_key, started):
    snapped = SendSnapshot.of(await send._askable(owner_id, chat_id))

    async def exclusive():
        chat = await send._askable(owner_id, chat_id)
        missed = snapped.missed(chat)
        if missed is not None:
            return await send.chats.commit_attempt(owner_id, chat_id, attempt_key, missed)
        return chat

    prepared = await send.chats.with_chat(chat_id, exclusive)
    if not hasattr(prepared, "document_id"):
        return prepared
    model = ListedModel.parse(outgoing.model, outgoing.model_present)
    if outgoing.tell:
        attempt = await send._tell(prepared, model.value, started)
    else:
        attempt = await send._spoken(prepared, outgoing, model.value, started)
    return await send.chats.commit_attempt(owner_id, chat_id, attempt_key, attempt)
