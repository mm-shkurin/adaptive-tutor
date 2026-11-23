import { failureText } from '../../../shared/api/failureText'
import { httpErrorIn } from '../../../shared/api/httpResponse'

export const QUESTION_COUNTS = [3, 5, 8]
export const DEFAULT_QUESTION_COUNT = 5
export const TOPIC_MAX = 200

export const EMPTY_TOPIC = 'Тема пустая.'
export const TOPIC_TOO_LONG = 'Тема длиннее 200 символов.'
export const NO_READY_PDF = 'Для викторины нужен готовый PDF.'
export const BAD_COUNT = 'Число вопросов — 3, 5 или 8.'
export const ASSEMBLE_FAILED = 'Не удалось собрать викторину.'
export const DOCUMENTS_UNAVAILABLE = 'Не удалось открыть документы.'

const CREATE_FAILURE = {
  empty_topic: EMPTY_TOPIC,
  invalid_question_count: BAD_COUNT,
  no_ready_document: NO_READY_PDF,
  document_not_ready: NO_READY_PDF,
  empty_retrieval: ASSEMBLE_FAILED,
  generation_failed: ASSEMBLE_FAILED,
}

export function readyPdfChoices(pageOrDocs) {
  const documents = Array.isArray(pageOrDocs) ? pageOrDocs : (pageOrDocs?.documents ?? [])
  return documents
    .filter((doc) => doc.status === 'ready')
    .map((doc) => ({ id: doc.id, name: doc.name }))
}

export function createFormNotice({ documentsFailed, pdfCount }) {
  if (documentsFailed) return { id: 'quiz-documents-error', text: DOCUMENTS_UNAVAILABLE }
  if (pdfCount === 0) return { id: 'quiz-needs-pdf', text: NO_READY_PDF }
  return null
}

export function validateCreate({ documentId, topic, questionCount, readyIds }) {
  const ready = readyIds ?? []
  if (ready.length === 0 || !documentId || !ready.includes(documentId)) {
    return refusal('no_ready_document', NO_READY_PDF)
  }
  const trimmed = typeof topic === 'string' ? topic.trim() : ''
  if (!trimmed) return refusal('empty_topic', EMPTY_TOPIC)
  if (trimmed.length > TOPIC_MAX) return refusal('empty_topic', TOPIC_TOO_LONG)
  const count = questionCount == null ? DEFAULT_QUESTION_COUNT : questionCount
  if (!QUESTION_COUNTS.includes(count)) return refusal('invalid_question_count', BAD_COUNT)
  return {
    ok: true,
    body: {
      document_id: documentId,
      topic: trimmed,
      question_count: count,
    },
  }
}

export function createFailureMessage(error) {
  const code = httpErrorIn(error)?.errorCode
  if (code && CREATE_FAILURE[code]) return CREATE_FAILURE[code]
  return failureText(error)
}

function refusal(code, message) {
  return { ok: false, code, message }
}
