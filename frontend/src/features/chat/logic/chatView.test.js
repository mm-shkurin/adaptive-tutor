import { describe, expect, it } from 'vitest'
import {
  chatScreenView,
  pageCitation,
  sourcePageLabel,
  sourcesFromLines,
  threadLines,
} from './chatView'

describe('chatView', () => {
  it('cites a page number and never a slide', () => {
    expect(pageCitation(5)).toBe('страница 5')
    expect(pageCitation(5)).not.toMatch(/слайд/i)
    expect(pageCitation(null)).toBeNull()
    expect(sourcePageLabel(12)).toBe('страница 12')
  })

  it('maps person and tutor lines with model and page', () => {
    const lines = threadLines([
      { id: 'p1', role: 'person', text: 'Что такое λ?' },
      {
        id: 't1',
        role: 'tutor',
        text: 'Скаляр.',
        model: 'qwen/qwen3-32b',
        page: 5,
        sources: [{ page: 5, text: 'λ — собственное число' }],
      },
    ])
    expect(lines[0]).toMatchObject({
      roleLabel: 'Вы',
      cssRole: 'user',
      text: 'Что такое λ?',
      citation: null,
    })
    expect(lines[1]).toMatchObject({
      roleLabel: 'AI-тьютор',
      cssRole: 'agent',
      text: 'Скаляр.',
      model: 'qwen/qwen3-32b',
      citation: 'страница 5',
    })
    expect(sourcesFromLines([
      { id: 'p1', role: 'person', text: 'q' },
      {
        id: 't1',
        role: 'tutor',
        text: 'a',
        sources: [{ page: 5, text: 'λ — собственное число' }],
      },
    ])).toEqual([{ key: 't1-0', pageLabel: 'страница 5', text: 'λ — собственное число' }])
  })

  it('builds list rows and empty sources when there is no tutor material', () => {
    const view = chatScreenView({
      summaries: [
        {
          id: 'c1',
          document_id: 'd1',
          document_name: 'Матанализ.pdf',
          preview: 'Что такое λ?',
        },
      ],
      chat: {
        id: 'c1',
        document_id: 'd1',
        document_name: 'Матанализ.pdf',
        askable: true,
        notice: null,
        lines: [{ id: 'p1', role: 'person', text: 'Что такое λ?' }],
      },
    })
    expect(view.rows[0]).toEqual({
      id: 'c1',
      documentName: 'Матанализ.pdf',
      preview: 'Что такое λ?',
    })
    expect(view.sources).toEqual([])
    expect(view.heading).toBe('Чат с AI-тьютором')
  })
})
