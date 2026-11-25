import { send } from '../send'
import { isPresentationBody } from './bodyGuards'
import { UPLOAD_TIMEOUT_MS } from './documentApi'
import { BACKEND } from './paths'

export function createPresentation(title, signal) {
  const body = title === undefined ? {} : { title }
  return send(BACKEND.presentations.create, {
    method: 'POST',
    body,
    signal,
    guard: isPresentationBody,
  })
}

export function addSlides(id, files, idempotencyKey, signal) {
  const form = new FormData()
  for (const file of files) {
    form.append('images', file)
  }
  return send(BACKEND.presentations.slides(id), {
    method: 'POST',
    body: form,
    signal,
    timeoutMs: UPLOAD_TIMEOUT_MS,
    headers: { 'Idempotency-Key': idempotencyKey },
    guard: isPresentationBody,
  })
}

export function indexPresentation(id, idempotencyKey, signal) {
  return send(BACKEND.presentations.index(id), {
    method: 'POST',
    signal,
    headers: { 'Idempotency-Key': idempotencyKey },
    guard: isPresentationBody,
  })
}