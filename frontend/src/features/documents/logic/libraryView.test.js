import { describe, expect, it } from 'vitest'
import { libraryView } from './libraryView'

const readyDocument = {
  id: '11111111-1111-1111-1111-111111111111',
  name: 'Матанализ.pdf',
  kind: 'pdf',
  size_bytes: 8703180,
  page_count: 98,
  piece_count: 67,
  status: 'ready',
  error: null,
}

const waitingDocument = {
  id: '22222222-2222-2222-2222-222222222222',
  name: 'Алгебра.pdf',
  kind: 'pdf',
  size_bytes: 4299161,
  page_count: null,
  piece_count: null,
  status: 'waiting',
  error: null,
}

describe('libraryView', () => {
  it('An empty library shows the PDF door and no materials', () => {
    expect(libraryView({ documents: [], has_next: false })).toEqual({
      heading: 'Документы',
      pdfDoor: {
        title: 'Загрузить PDF',
        hint: 'до 50 MB · парсинг и индексация',
      },
      presentationDoor: 'Создать презентацию',
      emptyList: 'Пока нет материалов',
      rows: [],
    })
  })

  it('A ready document shows its name, size, pages, and piece count', () => {
    const view = libraryView({ documents: [readyDocument], has_next: false })
    expect(view.emptyList).toBeNull()
    expect(view.rows).toEqual([
      {
        id: readyDocument.id,
        name: 'Матанализ.pdf',
        meta: '8.3 MB · 98 стр. · 67 чанков',
        statusLabel: 'Готов',
        statusPill: 'ready',
        kind: 'pdf',
        failureReason: null,
        canDelete: false,
      },
    ])
  })

  it('A failed document shows the failure and the reason', () => {
    const failed = {
      id: '33333333-3333-3333-3333-333333333333',
      name: 'Методичка.pdf',
      kind: 'pdf',
      size_bytes: 2202009,
      page_count: null,
      piece_count: null,
      status: 'failed',
      error: 'Не удалось прочитать страницу 12',
    }
    const view = libraryView({ documents: [failed], has_next: false })
    expect(view.emptyList).toBeNull()
    expect(view.rows[0]).toEqual({
      id: failed.id,
      name: 'Методичка.pdf',
      meta: 'Не удалось прочитать страницу 12',
      statusLabel: 'Не удалось',
      statusPill: 'failed',
      kind: 'pdf',
      failureReason: 'Не удалось прочитать страницу 12',
      canDelete: false,
    })
  })

  it('A waiting document shows waiting meta and label', () => {
    const view = libraryView({ documents: [waitingDocument], has_next: false })
    expect(view.rows[0]).toEqual({
      id: waitingDocument.id,
      name: 'Алгебра.pdf',
      meta: '4.1 MB · ждёт индексации',
      statusLabel: 'Ждёт',
      statusPill: 'waiting',
      kind: 'pdf',
      failureReason: null,
      canDelete: false,
    })
  })

  it('A draft presentation row shows title, draft pill, and delete', () => {
    const draft = {
      id: '44444444-4444-4444-4444-444444444444',
      name: 'LinAlg',
      kind: 'presentation',
      size_bytes: 0,
      page_count: null,
      piece_count: null,
      status: 'draft',
      error: null,
    }
    const view = libraryView({ documents: [draft], has_next: false })
    expect(view.rows[0]).toEqual({
      id: draft.id,
      name: 'LinAlg',
      meta: 'черновик',
      statusLabel: 'Черновик',
      statusPill: 'draft',
      kind: 'presentation',
      failureReason: null,
      canDelete: true,
    })
  })

  it('A failed presentation row shows the index error reason', () => {
    const failed = {
      id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa4',
      name: 'LinAlg',
      kind: 'presentation',
      size_bytes: 0,
      page_count: null,
      piece_count: null,
      status: 'failed',
      error: 'ocr refused',
      created_at: '2024-05-06T07:08:09Z',
    }
    const view = libraryView({ documents: [failed], has_next: false })
    expect(view.rows[0]).toMatchObject({
      statusLabel: 'Не удалось',
      statusPill: 'failed',
      meta: 'ocr refused',
      failureReason: 'ocr refused',
    })
  })

  it('A ready presentation row shows title, ready pill, and piece meta without null pages', () => {
    const readyPresentation = {
      id: '55555555-5555-5555-5555-555555555555',
      name: 'LinAlg',
      kind: 'presentation',
      size_bytes: 0,
      page_count: null,
      piece_count: 3,
      status: 'ready',
      error: null,
    }
    const view = libraryView({ documents: [readyPresentation], has_next: false })
    expect(view.rows[0]).toEqual({
      id: readyPresentation.id,
      name: 'LinAlg',
      meta: '3 чанков',
      statusLabel: 'Готов',
      statusPill: 'ready',
      kind: 'presentation',
      failureReason: null,
      canDelete: true,
    })
  })
})
