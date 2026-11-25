const OPTION_KEYS = ['A', 'B', 'C', 'D']

export function pageCitation(page) {
  if (typeof page !== 'number') return null
  return `страница ${page}`
}

export function quizCitation(question) {
  if (question == null) return null
  if (question.slide != null) {
    if (question.page != null) return `Слайд ${question.slide}, стр. ${question.page}`
    return `Слайд ${question.slide}`
  }
  return pageCitation(question.page)
}

export function quizCiteTestId(question) {
  if (question == null) return null
  return question.slide != null ? 'quiz-cite-slide' : 'quiz-cite-page'
}

export function questionCountLabel(count) {
  if (count === 3) return '3 вопроса'
  return `${count} вопросов`
}

export function scoreLabel(score) {
  if (!score) return null
  return `${score.correct} / ${score.total}`
}

export function lastScoreText(score) {
  const label = scoreLabel(score)
  if (!label) return null
  return `Прошлый результат: ${label}`
}

export function isWeakScore(score) {
  return Boolean(score) && score.correct < score.total
}

export function scoreBadgeClass(weak) {
  return weak ? 'quiz-score-badge weak' : 'quiz-score-badge'
}

export function cardRows(quizzes) {
  return quizzes.map((quiz) => ({
    id: quiz.id,
    documentName: quiz.document_name,
    topic: quiz.topic,
    countLabel: questionCountLabel(quiz.question_count),
    scoreText: lastScoreText(quiz.last_score),
    scoreClass: scoreBadgeClass(isWeakScore(quiz.last_score)),
  }))
}

export function withQuizCard(rows, detail) {
  const card = {
    id: detail.id,
    document_id: detail.document_id,
    document_name: detail.document_name,
    topic: detail.topic,
    question_count: detail.question_count,
    last_score: detail.last_score ?? null,
  }
  if (!rows.some((row) => row.id === card.id)) return [card, ...rows]
  return rows.map((row) => (row.id === card.id ? card : row))
}

export function screenView({ isNew, quizId, quiz }) {
  if (isNew) return 'create'
  if (!quizId) return 'list'
  if (quiz?.id !== quizId) return 'opening'
  if (quiz.status === 'take') return 'take'
  if (quiz.status === 'result') return 'result'
  return 'opening'
}

export function currentQuestion(detail) {
  if (!detail || detail.status !== 'take') return null
  if (typeof detail.current_index !== 'number') return null
  return detail.questions[detail.current_index] ?? null
}

export function isAnswered(question) {
  return Boolean(question?.chosen_choice_id)
}

export function shouldSendChoice(question) {
  return Boolean(question) && !isAnswered(question)
}

export function shouldAdvance(question) {
  return isAnswered(question)
}

export function choiceMark(choiceId, question) {
  if (!isAnswered(question)) return null
  if (question.correct_choice_id && choiceId === question.correct_choice_id) return 'correct'
  if (choiceId === question.chosen_choice_id && question.correct === true) return 'correct'
  if (choiceId === question.chosen_choice_id && question.correct === false) return 'wrong'
  return null
}

export function choiceClass(mark) {
  if (mark === 'correct') return 'quiz-option correct'
  if (mark === 'wrong') return 'quiz-option wrong'
  return 'quiz-option'
}

export function optionKey(index) {
  return OPTION_KEYS[index] ?? ''
}

export function gradeLabel(question) {
  if (!isAnswered(question) || typeof question.correct !== 'boolean') return null
  return question.correct ? 'Верно.' : 'Неверно.'
}

export function progressPercent(detail) {
  const question = currentQuestion(detail)
  if (!question) return 0
  const total = detail.questions.length
  const done = isAnswered(question) ? detail.current_index + 1 : detail.current_index
  return Math.round((done / total) * 100)
}

export function positionLabel(index, total) {
  return `Вопрос ${index + 1} из ${total}`
}

export function questionNumberLabel(index) {
  return `Вопрос ${index + 1}`
}

export function advanceLabel(detail) {
  const index = detail?.current_index ?? 0
  const total = detail?.questions?.length ?? 0
  return index >= total - 1 ? 'Завершить' : 'Далее'
}

export function takeView(detail) {
  const question = currentQuestion(detail)
  if (!question) return null
  const index = detail.current_index
  const total = detail.questions.length
  const answered = isAnswered(question)
  return {
    topic: detail.topic,
    position: positionLabel(index, total),
    number: questionNumberLabel(index),
    text: question.text,
    progress: progressPercent(detail),
    answered,
    canAdvance: shouldAdvance(question),
    grade: gradeLabel(question),
    cite: answered ? quizCitation(question) : null,
    citeTestId: answered ? quizCiteTestId(question) : null,
    advance: advanceLabel(detail),
    choices: question.choices.map((choice, choiceIndex) => {
      const mark = choiceMark(choice.id, question)
      return {
        id: choice.id,
        key: optionKey(choiceIndex),
        text: choice.text,
        mark,
        className: choiceClass(mark),
      }
    }),
  }
}

export function resultSubtitle(score) {
  if (score && score.correct === score.total) return 'Все ответы верные.'
  return 'Разбор ответов по вопросам.'
}

export function reviewItemClass(ok) {
  return ok ? 'quiz-review-item ok' : 'quiz-review-item bad'
}

function choiceText(question, id) {
  if (!id) return ''
  return question.choices.find((choice) => choice.id === id)?.text ?? ''
}

export function reviewRows(detail) {
  return (detail?.questions ?? []).map((question, index) => ({
    id: question.id,
    number: index + 1,
    text: question.text,
    ok: question.correct === true,
    itemClass: reviewItemClass(question.correct === true),
    chosenText: choiceText(question, question.chosen_choice_id),
    correctText: choiceText(question, question.correct_choice_id),
    pageLabel: quizCitation(question),
  }))
}

export function resultView(detail) {
  if (!detail || detail.status !== 'result') return null
  return {
    score: scoreLabel(detail.last_score) ?? '—',
    subtitle: resultSubtitle(detail.last_score),
    rows: reviewRows(detail),
  }
}

export function missingQuizText(errorCode, status) {
  if (status === 404 || errorCode === 'quiz_not_found') return 'Викторина не найдена.'
  return null
}
