import { describe, expect, it } from 'vitest'
import {
  createListEpoch,
  createSubmission,
  fresherPage,
  needsStatusStream,
  pageWithStatusEvent,
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

  it('needsStatusStream is true while waiting or indexing', () => {
    expect(needsStatusStream([ready])).toBe(false)
    expect(needsStatusStream([waiting, ready])).toBe(true)
    expect(needsStatusStream([{ ...waiting, status: 'indexing' }])).toBe(true)
  })

  it('pageWithStatusEvent applies a newer status to the matching row', () => {
    const page = { documents: [waiting, ready], has_next: false }
    const indexing = { ...waiting, status: 'indexing' }
    const next = pageWithStatusEvent(page, indexing)
    expect(next.documents[0].status).toBe('indexing')
    expect(next.documents[1]).toEqual(ready)
    const stale = pageWithStatusEvent(
      { documents: [{ ...waiting, status: 'ready', page_count: 1, piece_count: 1 }], has_next: false },
      indexing
    )
    expect(stale.documents[0].status).toBe('ready')
  })

  it('pageWithStatusEvent inserts a document that the page does not have yet', () => {
    const page = { documents: [ready], has_next: false }
    const next = pageWithStatusEvent(page, waiting)
    expect(next.documents.map((document) => document.id)).toEqual([waiting.id, ready.id])
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

  it('fresherPage keeps a just-uploaded in-flight row missing from a late list', () => {
    const page = { documents: [waiting, ready], has_next: false }
    const lateList = { documents: [ready], has_next: false }
    expect(fresherPage(page, lateList).documents.map((document) => document.id)).toEqual([
      waiting.id,
      ready.id,
    ])
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

  it('Applying the same status event twice leaves the row status unchanged', () => {
    const page = { documents: [waiting], has_next: false }
    const indexing = { ...waiting, status: 'indexing' }
    const once = pageWithStatusEvent(page, indexing)
    const twice = pageWithStatusEvent(once, indexing)
    expect(twice.documents[0].status).toBe('indexing')
    expect(twice.documents).toHaveLength(1)
  })
})
