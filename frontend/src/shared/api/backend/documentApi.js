import { send } from '../send'
import { isDocumentBody, isDocumentPageBody } from './bodyGuards'
import { BACKEND } from './paths'

/** Upload waits on virus scan (server budget 30s) plus transfer of up to 50 MB. */
export const UPLOAD_TIMEOUT_MS = 90_000

export function listDocuments(signal) {
  return send(BACKEND.documents.list, { signal, guard: isDocumentPageBody })
}

export function uploadDocument(file, idempotencyKey, signal) {
  const form = new FormData()
  form.append('file', file)
  return send(BACKEND.documents.list, {
    method: 'POST',
    body: form,
    signal,
    timeoutMs: UPLOAD_TIMEOUT_MS,
    headers: { 'Idempotency-Key': idempotencyKey },
    guard: isDocumentBody,
  })
}

export function readDocument(id, signal) {
  return send(BACKEND.documents.item(id), { signal, guard: isDocumentBody })
}
