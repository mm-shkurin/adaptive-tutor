import { send } from '../send'
import { isDocumentBody, isDocumentPageBody } from './bodyGuards'
import { BACKEND } from './paths'

export function listDocuments(signal) {
  return send(BACKEND.documents.list, { signal, guard: isDocumentPageBody })
}

export function uploadDocument(file, idempotencyKey) {
  const form = new FormData()
  form.append('file', file)
  return send(BACKEND.documents.list, {
    method: 'POST',
    body: form,
    headers: { 'Idempotency-Key': idempotencyKey },
    guard: isDocumentBody,
  })
}

export function readDocument(id, signal) {
  return send(BACKEND.documents.item(id), { signal, guard: isDocumentBody })
}
