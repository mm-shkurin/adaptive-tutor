import { describe, expect, it } from 'vitest'
import { libraryView } from './libraryView'

const readyDocument = {
  id: '11111111-1111-1111-1111-111111111111',
  name: 'Матанализ.pdf',
  size_bytes: 8703180,
  page_count: 98,
  piece_count: 67,
  status: 'ready',
  error: null,
}

const waitingDocument = {
  id: '22222222-2222-2222-2222-222222222222',
  name: 'Алгебра.pdf',
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
        failureReason: null,
      },
    ])
  })

  it('A waiting document shows waiting meta and label', () => {
    const view = libraryView({ documents: [waitingDocument], has_next: false })
    expect(view.rows[0]).toEqual({
      id: waitingDocument.id,
      name: 'Алгебра.pdf',
      meta: '4.1 MB · ждёт индексации',
      statusLabel: 'Ждёт',
      statusPill: 'waiting',
      failureReason: null,
    })
  })
})
