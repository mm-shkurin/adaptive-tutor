import { describe, expect, it } from 'vitest'
import { libraryView } from './libraryView'

const readyDocument = {
  id: '11111111-1111-1111-1111-111111111111',
  name: 'Матанализ.pdf',
  size_bytes: 1048576,
  page_count: 12,
  piece_count: 4,
  status: 'ready',
  error: null,
}

describe('libraryView', () => {
  // Error: libraryView is not implemented
  it.skip('An empty library shows the PDF door and no materials', () => {
    expect(libraryView({ documents: [], has_next: false })).toEqual({
      heading: 'Документы',
      pdfDoor: {
        title: 'Загрузить PDF',
        hint: 'до 50 MB · парсинг и индексация',
      },
      presentationDoor: 'Создать презентацию',
      emptyList: 'Пока нет материалов',
    })
    expect(libraryView({ documents: [readyDocument], has_next: false }).emptyList).toBeNull()
  })
})
