import { describe, expect, it } from 'vitest'
import { needsStatusPoll, pageWithUploaded } from './documentPage'

const ready = {
  id: '11111111-1111-1111-1111-111111111111',
  name: 'Матанализ.pdf',
  size_bytes: 1048576,
  page_count: 12,
  piece_count: 4,
  status: 'ready',
  error: null,
}

const waiting = {
  id: '22222222-2222-2222-2222-222222222222',
  name: 'Алгебра.pdf',
  size_bytes: 2097152,
  page_count: null,
  piece_count: null,
  status: 'waiting',
  error: null,
}

describe('documentPage', () => {
  it('An accepted PDF appears at the top as waiting', () => {
    const page = pageWithUploaded({ documents: [ready], has_next: false }, waiting)
    expect(page.documents.map((document) => document.id)).toEqual([waiting.id, ready.id])
    expect(page.documents[0].status).toBe('waiting')
  })

  it('needsStatusPoll is true while waiting or indexing', () => {
    expect(needsStatusPoll([ready])).toBe(false)
    expect(needsStatusPoll([waiting, ready])).toBe(true)
    expect(needsStatusPoll([{ ...waiting, status: 'indexing' }])).toBe(true)
  })
})
