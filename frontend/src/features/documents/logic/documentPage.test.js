import { describe, expect, it } from 'vitest'
import {
  createListEpoch,
  createSubmission,
  fresherPage,
  needsStatusPoll,
  pageWithUploaded,
  shouldApplyUpload,
} from './documentPage'

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

  it('A second press on one file adds one row', () => {
    const submission = createSubmission()
    expect(submission.begin('key-1')).toBe('key-1')
    expect(submission.begin('key-2')).toBeNull()
    const page = { documents: [ready], has_next: false }
    const once = pageWithUploaded(page, waiting)
    const twice = pageWithUploaded(once, waiting)
    expect(twice.documents.map((document) => document.id)).toEqual([waiting.id, ready.id])
    submission.finish()
    expect(submission.begin('key-3')).toBe('key-3')
  })

  it('An older status arriving late does not replace a newer one', () => {
    const epoch = createListEpoch()
    const older = epoch.start()
    const newer = epoch.start()
    const becameReady = { ...waiting, status: 'ready', page_count: 12, piece_count: 4 }
    const readyPage = { documents: [becameReady], has_next: false }
    const indexingPage = { documents: [{ ...waiting, status: 'indexing' }], has_next: false }
    expect(epoch.accepts(older)).toBe(false)
    expect(epoch.accepts(newer)).toBe(true)
    expect(fresherPage(readyPage, indexingPage).documents[0].status).toBe('ready')
    expect(fresherPage(indexingPage, readyPage).documents[0].status).toBe('ready')
  })

  it('Leaving before the upload is accepted leaves the list unchanged', () => {
    const page = { documents: [ready], has_next: false }
    expect(shouldApplyUpload(true)).toBe(false)
    expect(shouldApplyUpload(false)).toBe(true)
    expect(fresherPage(null, page)).toEqual(page)
  })
})
