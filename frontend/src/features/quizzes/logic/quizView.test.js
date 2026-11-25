import { describe, expect, it } from 'vitest'
import {
  advanceLabel,
  cardRows,
  choiceMark,
  pageCitation,
  quizCitation,
  quizCiteTestId,
  resultView,
  screenView,
  shouldAdvance,
  shouldSendChoice,
  takeView,
  withQuizCard,
} from './quizView'

function choice(id, text) {
  return { id, text }
}

function question(overrides = {}) {
  return {
    id: overrides.id ?? 'q0',
    text: overrides.text ?? 'Что такое производная?',
    choices: overrides.choices ?? [
      choice('a', 'Предел'),
      choice('b', 'Интеграл'),
      choice('c', 'Матрица'),
      choice('d', 'Вектор'),
    ],
    chosen_choice_id: overrides.chosen_choice_id ?? null,
    correct_choice_id: overrides.correct_choice_id ?? null,
    correct: overrides.correct ?? null,
    page: overrides.page ?? null,
    slide: overrides.slide ?? null,
  }
}

function detail(overrides = {}) {
  const questions = overrides.questions ?? [question(), question({ id: 'q1' }), question({ id: 'q2' })]
  return {
    id: 'quiz-1',
    document_id: 'pdf-1',
    document_name: 'Матанализ.pdf',
    topic: 'Производные',
    question_count: questions.length,
    status: 'take',
    last_score: { correct: 2, total: 5 },
    current_index: 0,
    questions,
    ...overrides,
  }
}

describe('quiz screens', () => {
  it('routes an open attempt to take and a finished quiz to the result', () => {
    expect(screenView({ isNew: false, quizId: null, quiz: null })).toBe('list')
    expect(screenView({ isNew: true, quizId: null, quiz: null })).toBe('create')
    expect(screenView({ isNew: false, quizId: 'quiz-1', quiz: null })).toBe('opening')
    expect(screenView({ isNew: false, quizId: 'quiz-1', quiz: detail() })).toBe('take')
    expect(screenView({
      isNew: false,
      quizId: 'quiz-1',
      quiz: detail({ status: 'result', current_index: undefined }),
    })).toBe('result')
  })

  it('shows the document, the topic, the count, and only the last completed score', () => {
    const [row] = cardRows([
      {
        id: 'quiz-1',
        document_name: 'Матанализ.pdf',
        topic: 'Производные',
        question_count: 5,
        last_score: { correct: 2, total: 5 },
      },
    ])
    expect(row).toMatchObject({
      documentName: 'Матанализ.pdf',
      topic: 'Производные',
      countLabel: '5 вопросов',
      scoreText: 'Прошлый результат: 2 / 5',
      scoreClass: 'quiz-score-badge weak',
    })
    expect(JSON.stringify(row)).not.toMatch(/слайд|~|мин|источник/i)
    const [unfinished] = cardRows([
      {
        id: 'quiz-2',
        document_name: 'Физика.pdf',
        topic: 'Кинематика',
        question_count: 3,
        last_score: null,
      },
    ])
    expect(unfinished.countLabel).toBe('3 вопроса')
    expect(unfinished.scoreText).toBeNull()
  })

  it('keeps the previous score in place when a new attempt starts', () => {
    const rows = [{
      id: 'quiz-1',
      document_id: 'pdf-1',
      document_name: 'Матанализ.pdf',
      topic: 'Производные',
      question_count: 5,
      last_score: { correct: 2, total: 5 },
    }]
    const next = withQuizCard(rows, detail({
      status: 'take',
      last_score: { correct: 2, total: 5 },
    }))
    expect(next).toHaveLength(1)
    expect(next[0].last_score).toEqual({ correct: 2, total: 5 })
  })
})

describe('take view', () => {
  it('hides the page and blocks next until a choice is stored', () => {
    const view = takeView(detail())
    expect(view.choices).toHaveLength(4)
    expect(view.choices.map((item) => item.key)).toEqual(['A', 'B', 'C', 'D'])
    expect(view.choices.every((item) => item.mark === null)).toBe(true)
    expect(view.cite).toBeNull()
    expect(view.grade).toBeNull()
    expect(view.canAdvance).toBe(false)
    expect(view.advance).toBe('Далее')
    expect(view.position).toBe('Вопрос 1 из 3')
    expect(view.progress).toBe(0)
    expect(shouldSendChoice(detail().questions[0])).toBe(true)
    expect(shouldAdvance(detail().questions[0])).toBe(false)
    expect(pageCitation(null)).toBeNull()
    expect(pageCitation(4)).toBe('страница 4')
    expect(pageCitation(4)).not.toMatch(/слайд/i)
  })

  it('marks a wrong choice and the correct one and reveals the page', () => {
    const view = takeView(detail({
      questions: [
        question({
          chosen_choice_id: 'b',
          correct_choice_id: 'a',
          correct: false,
          page: 4,
        }),
        question({ id: 'q1' }),
        question({ id: 'q2' }),
      ],
    }))
    expect(view.grade).toBe('Неверно.')
    expect(view.cite).toBe('страница 4')
    expect(view.citeTestId).toBe('quiz-cite-page')
    expect(view.canAdvance).toBe(true)
    expect(view.choices.find((item) => item.id === 'b').mark).toBe('wrong')
    expect(view.choices.find((item) => item.id === 'a').mark).toBe('correct')
    expect(shouldSendChoice(question({ chosen_choice_id: 'b' }))).toBe(false)
  })

  it('shows a slide citation when the question cites a deck slide', () => {
    const stored = question({
      chosen_choice_id: 'a',
      correct_choice_id: 'a',
      correct: true,
      slide: 2,
    })
    const view = takeView(detail({ questions: [stored] }))
    expect(view.cite).toBe('Слайд 2')
    expect(view.citeTestId).toBe('quiz-cite-slide')
    expect(quizCitation(stored)).toBe('Слайд 2')
    expect(quizCiteTestId(stored)).toBe('quiz-cite-slide')
  })

  it('marks only the correct choice when the answer is right', () => {
    const stored = question({
      chosen_choice_id: 'a',
      correct_choice_id: 'a',
      correct: true,
      page: 9,
    })
    expect(choiceMark('a', stored)).toBe('correct')
    expect(choiceMark('b', stored)).toBeNull()
    const view = takeView(detail({
      current_index: 2,
      questions: [question({ id: 'q0' }), question({ id: 'q1' }), stored],
    }))
    expect(view.grade).toBe('Верно.')
    expect(view.advance).toBe('Завершить')
    expect(view.cite).toBe('страница 9')
    expect(view.citeTestId).toBe('quiz-cite-page')
    expect(advanceLabel(detail({ current_index: 0 }))).toBe('Далее')
  })
})

describe('result view', () => {
  it('keeps script and SQL fragments as plain topic and choice text', () => {
    const script = '<script>alert(1)</script>'
    const sql = "' OR 1=1"
    const [row] = cardRows([{
      id: 'quiz-x',
      document_name: 'Матанализ.pdf',
      topic: `Тема ${script} ${sql}`,
      question_count: 3,
      last_score: null,
    }])
    expect(row.topic).toContain(script)
    expect(row.topic).toContain(sql)
    const view = takeView(detail({
      topic: `Тема ${script}`,
      questions: [
        question({
          text: `Вопрос ${script}`,
          choices: [
            choice('a', `A ${script}`),
            choice('b', `B ${sql}`),
            choice('c', 'C'),
            choice('d', 'D'),
          ],
        }),
      ],
    }))
    expect(view.text).toContain(script)
    expect(view.choices[0].text).toContain(script)
    expect(view.choices[1].text).toContain(sql)
  })

  it('shows the score and the chosen, correct, and page for every question', () => {
    const view = resultView(detail({
      status: 'result',
      current_index: undefined,
      last_score: { correct: 1, total: 3 },
      questions: [
        question({
          id: 'q0',
          text: 'Первый',
          chosen_choice_id: 'a',
          correct_choice_id: 'a',
          correct: true,
          page: 2,
        }),
        question({
          id: 'q1',
          text: 'Второй',
          chosen_choice_id: 'b',
          correct_choice_id: 'c',
          correct: false,
          page: 6,
        }),
        question({
          id: 'q2',
          text: 'Третий',
          chosen_choice_id: 'd',
          correct_choice_id: 'd',
          correct: true,
          page: 8,
        }),
      ],
    }))
    expect(view.score).toBe('1 / 3')
    expect(view.rows).toHaveLength(3)
    expect(view.rows[1]).toMatchObject({
      text: 'Второй',
      chosenText: 'Интеграл',
      correctText: 'Матрица',
      pageLabel: 'страница 6',
      ok: false,
    })
    expect(view.rows.every((row) => row.pageLabel && !/слайд/i.test(row.pageLabel))).toBe(true)
  })
})
