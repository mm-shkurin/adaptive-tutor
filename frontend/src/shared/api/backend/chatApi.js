import { send } from '../send'
import {
  isChatBody,
  isChatListBody,
  isSendResultBody,
} from './bodyGuards'
import { BACKEND } from './paths'

export function listChats(signal) {
  return send(BACKEND.chats.list, { signal, guard: isChatListBody })
}

export function getChat(id, signal) {
  return send(BACKEND.chats.item(id), { signal, guard: isChatBody })
}

export function createChat(documentId, signal) {
  const body = documentId ? { document_id: documentId } : {}
  return send(BACKEND.chats.list, {
    method: 'POST',
    body,
    signal,
    guard: isChatBody,
  })
}

export function openChat(documentId, signal) {
  return send(BACKEND.chats.open, {
    method: 'POST',
    body: { document_id: documentId },
    signal,
    guard: isChatBody,
  })
}

export function sendChatMessage(chatId, payload, idempotencyKey, signal) {
  return send(BACKEND.chats.messages(chatId), {
    method: 'POST',
    body: payload,
    headers: { 'Idempotency-Key': idempotencyKey },
    signal,
    // Live freellmapi often needs 20–40s; default REQUEST_TIMEOUT_MS is 15s.
    timeoutMs: 90_000,
    guard: isSendResultBody,
  })
}
