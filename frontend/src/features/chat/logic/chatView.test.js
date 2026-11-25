import { describe, expect, it } from 'vitest'
import {
  chatScreenView,
  gradeLabel,
  isWithholding,
  openExaminerQuestion,
  pageCitation,
  replyCitation,
  sourcePageLabel,
  sourcesFromLines,
  threadLines,
} from './chatView'

describe('chatView', () => {
  it('cites a page number and never a slide', () => {
    expect(pageCitation(5)).toBe('страница 5')
    expect(pageCitation(5)).not.toMatch(/слайд/i)
    expect(pageCitation(null)).toBeNull()
    expect(sourcePageLabel({ page: 12 })).toBe('страница 12')
  })

  it('formats slide citations for presentations', () => {
    expect(sourcePageLabel({ slide: 1, page: null })).toBe('Слайд 1')
    expect(sourcePageLabel({ slide: 2, page: 5 })).toBe('Слайд 2, стр. 5')
    expect(
      replyCitation({
        page: null,
        sources: [{ slide: 1, page: null, text: 't' }],
      }),
    ).toBe('Слайд 1')
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
    expect(
      threadLines([
        {
          id: 't2',
          role: 'tutor',
          text: 'Ответ',
          sources: [{ slide: 3, page: null, text: 'deck' }],
        },
      ])[0].citation,
    ).toBe('Слайд 3')
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

  it('maps examiner question choices and grade labels without a page on the question', () => {
    const graded = threadLines([
      {
        id: 'q0',
        role: 'tutor',
        text: 'Old?',
        kind: 'question',
        page: null,
        choices: [
          { id: 'x1', text: 'X' },
          { id: 'x2', text: 'Y' },
          { id: 'x3', text: 'Z' },
          { id: 'x4', text: 'W' },
        ],
      },
      {
        id: 'g1',
        role: 'tutor',
        text: '',
        kind: 'grade',
        correct: true,
        choice_id: 'x1',
        page: 4,
      },
    ])
    expect(graded[0].choices).toHaveLength(4)
    expect(graded[1].gradeLabel).toBe('Верно')
    expect(graded[1].citation).toBe('страница 4')

    const open = threadLines([
      {
        id: 'q1',
        role: 'tutor',
        text: 'Which process?',
        kind: 'question',
        page: null,
        choices: [
          { id: 'c1', text: 'A' },
          { id: 'c2', text: 'B' },
          { id: 'c3', text: 'C' },
          { id: 'c4', text: 'D' },
        ],
      },
    ])
    expect(open[0].citation).toBeNull()
    expect(open[0].choices).toHaveLength(4)
    expect(gradeLabel({ kind: 'grade', correct: false })).toBe('Неверно')
    expect(isWithholding([{ role: 'tutor', kind: 'withheld' }])).toBe(true)
    expect(openExaminerQuestion([{ role: 'tutor', kind: 'question', id: 'q1' }]).id).toBe('q1')
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
