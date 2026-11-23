import { describe, expect, it } from 'vitest'
import { RequestTimeoutError } from '../../../shared/api/requestTimeout'
import {
  ASSEMBLE_FAILED,
  BAD_COUNT,
  DEFAULT_QUESTION_COUNT,
  DOCUMENTS_UNAVAILABLE,
  EMPTY_TOPIC,
  NO_READY_PDF,
  QUESTION_COUNTS,
  TOPIC_TOO_LONG,
  createFailureMessage,
  createFormNotice,
  readyPdfChoices,
  validateCreate,
} from './createQuiz'

const ready = [{ id: 'pdf-1', name: 'Матанализ.pdf' }]

describe('readyPdfChoices', () => {
  it('keeps only ready PDFs', () => {
    const choices = readyPdfChoices({
      documents: [
        { id: '1', name: 'ready.pdf', status: 'ready' },
        { id: '2', name: 'waiting.pdf', status: 'waiting' },
        { id: '3', name: 'indexing.pdf', status: 'indexing' },
        { id: '4', name: 'failed.pdf', status: 'failed' },
      ],
    })
    expect(choices).toEqual([{ id: '1', name: 'ready.pdf' }])
  })
})

describe('validateCreate', () => {
  it('offers 3, 5, and 8 and defaults a missing count to five', () => {
    expect(QUESTION_COUNTS).toEqual([3, 5, 8])
    expect(DEFAULT_QUESTION_COUNT).toBe(5)
    const result = validateCreate({
      documentId: 'pdf-1',
      topic: '  производные  ',
      questionCount: undefined,
      readyIds: ['pdf-1'],
    })
    expect(result).toEqual({
      ok: true,
      body: { document_id: 'pdf-1', topic: 'производные', question_count: 5 },
    })
  })

  it('refuses a blank topic without a request body', () => {
    const result = validateCreate({
      documentId: 'pdf-1',
      topic: '   ',
      questionCount: 5,
      readyIds: ['pdf-1'],
    })
    expect(result.ok).toBe(false)
    expect(result.message).toBe(EMPTY_TOPIC)
    expect(result.body).toBeUndefined()
  })

  it('refuses a topic longer than 200 characters', () => {
    const result = validateCreate({
      documentId: 'pdf-1',
      topic: 'а'.repeat(201),
      questionCount: 5,
      readyIds: ['pdf-1'],
    })
    expect(result.message).toBe(TOPIC_TOO_LONG)
  })

  it('refuses a count outside 3, 5, and 8', () => {
    const result = validateCreate({
      documentId: 'pdf-1',
      topic: 'тема',
      questionCount: 4,
      readyIds: ['pdf-1'],
    })
    expect(result.message).toBe(BAD_COUNT)
  })

  it('refuses create when no ready PDF is selected', () => {
    expect(validateCreate({
      documentId: '',
      topic: 'тема',
      questionCount: 5,
      readyIds: [],
    }).message).toBe(NO_READY_PDF)
    expect(validateCreate({
      documentId: 'other',
      topic: 'тема',
      questionCount: 5,
      readyIds: ready.map((item) => item.id),
    }).message).toBe(NO_READY_PDF)
  })
})

describe('createFormNotice', () => {
  it('names a missing ready PDF and a document list failure', () => {
    expect(createFormNotice({ documentsFailed: false, pdfCount: 0 }).text).toBe(NO_READY_PDF)
    expect(createFormNotice({ documentsFailed: true, pdfCount: 0 }).text).toBe(DOCUMENTS_UNAVAILABLE)
    expect(createFormNotice({ documentsFailed: false, pdfCount: 2 })).toBeNull()
  })
})

describe('createFailureMessage', () => {
  it('says the quiz could not be assembled when generation fails', () => {
    const error = new Error('bad shape')
    error.status = 400
    error.errorCode = 'generation_failed'
    const wrapped = new Error('wrapped', { cause: error })
    expect(createFailureMessage(wrapped)).toBe(ASSEMBLE_FAILED)
    const empty = new Error('none')
    empty.status = 400
    empty.errorCode = 'empty_retrieval'
    expect(createFailureMessage(empty)).toBe(ASSEMBLE_FAILED)
  })

  it('keeps the timeout text when the server does not answer', () => {
    const wrapped = new Error('wrapped', { cause: new RequestTimeoutError(90000) })
    expect(createFailureMessage(wrapped)).toMatch(/не ответил/)
  })
})
