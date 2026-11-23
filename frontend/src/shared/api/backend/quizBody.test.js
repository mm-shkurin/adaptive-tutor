import { describe, expect, it } from 'vitest'
import { isQuizDetailBody, isQuizListBody } from './bodyGuards'

function choice(id) {
  return { id, text: id }
}

function question(id, answered) {
  return {
    id,
    text: `Вопрос ${id}`,
    choices: [choice('a'), choice('b'), choice('c'), choice('d')],
    chosen_choice_id: answered ? 'a' : null,
    correct_choice_id: answered ? 'a' : null,
    correct: answered ? true : null,
    page: answered ? 3 : null,
  }
}

function detail(overrides = {}) {
  return {
    id: 'quiz-1',
    document_id: 'pdf-1',
    document_name: 'Матанализ.pdf',
    topic: 'Производные',
    question_count: 3,
    status: 'take',
    last_score: null,
    current_index: 0,
    questions: [question('q0', false), question('q1', false), question('q2', false)],
    ...overrides,
  }
}

describe('quiz body guards', () => {
  it('accepts a list card and a take body with the page hidden', () => {
    expect(isQuizListBody({
      quizzes: [{
        id: 'quiz-1',
        document_id: 'pdf-1',
        document_name: 'Матанализ.pdf',
        topic: 'Производные',
        question_count: 5,
        last_score: { correct: 2, total: 5 },
      }],
    })).toBe(true)
    expect(isQuizDetailBody(detail())).toBe(true)
  })

  it('accepts a result without a current index and rejects a short choice list', () => {
    const finished = detail({
      status: 'result',
      current_index: undefined,
      last_score: { correct: 3, total: 3 },
      questions: [question('q0', true), question('q1', true), question('q2', true)],
    })
    expect(isQuizDetailBody(finished)).toBe(true)
    const broken = detail()
    broken.questions[0] = { ...broken.questions[0], choices: [choice('a'), choice('b')] }
    expect(isQuizDetailBody(broken)).toBe(false)
    expect(isQuizDetailBody(detail({ status: 'draft' }))).toBe(false)
  })
})
