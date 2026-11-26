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

export function getPresentation(id, signal) {
  return send(BACKEND.presentations.item(id), {
    method: 'GET',
    signal,
    guard: isPresentationBody,
  })
}

export function patchPresentation(id, body, signal) {
  return send(BACKEND.presentations.item(id), {
    method: 'PATCH',
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

export function addSlidesOfficeFile(id, file, idempotencyKey, signal) {
  const form = new FormData()
  form.append('file', file)
  return send(BACKEND.presentations.slides(id), {
    method: 'POST',
    body: form,
    signal,
    timeoutMs: UPLOAD_TIMEOUT_MS,
    headers: { 'Idempotency-Key': idempotencyKey },
    guard: isPresentationBody,
  })
}

export function addSlidesPdfPages(id, pdfDocumentId, pages, idempotencyKey, signal) {
  const form = new FormData()
  form.append('pdf_document_id', pdfDocumentId)
  form.append('pdf_pages', JSON.stringify(pages))
  return send(BACKEND.presentations.slides(id), {
    method: 'POST',
    body: form,
    signal,
    headers: { 'Idempotency-Key': idempotencyKey },
    guard: isPresentationBody,
  })
}

export function deletePresentation(id, signal) {
  return send(BACKEND.presentations.item(id), {
    method: 'DELETE',
    signal,
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