import { describe, expect, it } from 'vitest'
import { parsePdfPageList, readyPdfMaterials } from './presentationPdfSlides'

const readyPdf = {
  id: 'a',
  kind: 'pdf',
  status: 'ready',
  page_count: 5,
}

describe('presentationPdfSlides', () => {
  it('readyPdfMaterials keeps only ready PDFs', () => {
    expect(
      readyPdfMaterials([
        readyPdf,
        { id: 'b', kind: 'pdf', status: 'waiting' },
        { id: 'c', kind: 'presentation', status: 'ready' },
      ])
    ).toEqual([readyPdf])
  })

  it('parsePdfPageList dedupes and caps by page count', () => {
    expect(parsePdfPageList('1, 3, 3, 9', 5)).toEqual([1, 3])
    expect(parsePdfPageList('2;4', 10)).toEqual([2, 4])
    expect(parsePdfPageList('nope', 3)).toEqual([])
  })
})