function isRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

export function isTokenPairBody(value) {
  return isRecord(value) && typeof value.access_token === 'string' && typeof value.refresh_token === 'string'
}

export function isProfileBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    typeof value.email === 'string' &&
    typeof value.created_at === 'string' &&
    (value.avatar_url === null || typeof value.avatar_url === 'string')
  )
}

const DOCUMENT_STATUSES = new Set(['waiting', 'indexing', 'ready', 'failed'])

export function isDocumentBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    typeof value.size_bytes === 'number' &&
    (value.page_count === null || typeof value.page_count === 'number') &&
    (value.piece_count === null || typeof value.piece_count === 'number') &&
    DOCUMENT_STATUSES.has(value.status) &&
    (value.error === null || typeof value.error === 'string')
  )
}

export function isDocumentPageBody(value) {
  return (
    isRecord(value) &&
    Array.isArray(value.documents) &&
    value.documents.every(isDocumentBody) &&
    typeof value.has_next === 'boolean'
  )
}

export function isChatSummaryBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.document_id === 'string' &&
    typeof value.document_name === 'string' &&
    (value.preview === null || typeof value.preview === 'string')
  )
}

export function isChatListBody(value) {
  return isRecord(value) && Array.isArray(value.chats) && value.chats.every(isChatSummaryBody)
}

export function isSourceBody(value) {
  return (
    isRecord(value) &&
    typeof value.text === 'string' &&
    (value.page === null || value.page === undefined || typeof value.page === 'number')
  )
}

export function isChoiceBody(value) {
  return isRecord(value) && typeof value.id === 'string' && typeof value.text === 'string'
}

export function isLineBody(value) {
  if (
    !(
      isRecord(value) &&
      typeof value.id === 'string' &&
      (value.role === 'person' || value.role === 'tutor') &&
      typeof value.text === 'string'
    )
  ) {
    return false
  }
  if (
    value.kind !== undefined &&
    value.kind !== null &&
    value.kind !== 'question' &&
    value.kind !== 'grade' &&
    value.kind !== 'withheld' &&
    value.kind !== 'reply'
  ) {
    return false
  }
  if (value.choices !== undefined && value.choices !== null) {
    if (!Array.isArray(value.choices) || !value.choices.every(isChoiceBody)) return false
  }
  if (value.correct !== undefined && value.correct !== null && typeof value.correct !== 'boolean') {
    return false
  }
  if (
    value.choice_id !== undefined &&
    value.choice_id !== null &&
    typeof value.choice_id !== 'string'
  ) {
    return false
  }
  return true
}

export function isChatBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.document_id === 'string' &&
    typeof value.document_name === 'string' &&
    typeof value.askable === 'boolean' &&
    (value.notice === null || typeof value.notice === 'string') &&
    Array.isArray(value.lines) &&
    value.lines.every(isLineBody)
  )
}

const QUIZ_COUNTS = new Set([3, 5, 8])

function isNullableString(value) {
  return value === undefined || value === null || typeof value === 'string'
}

function isQuizScoreBody(value) {
  return isRecord(value) && typeof value.correct === 'number' && QUIZ_COUNTS.has(value.total)
}

export function isQuizCardBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.document_id === 'string' &&
    typeof value.document_name === 'string' &&
    typeof value.topic === 'string' &&
    QUIZ_COUNTS.has(value.question_count) &&
    (value.last_score === null || isQuizScoreBody(value.last_score))
  )
}

export function isQuizListBody(value) {
  return isRecord(value) && Array.isArray(value.quizzes) && value.quizzes.every(isQuizCardBody)
}

function isQuizQuestionBody(value) {
  if (!isRecord(value) || typeof value.id !== 'string' || typeof value.text !== 'string') return false
  if (!Array.isArray(value.choices) || value.choices.length !== 4 || !value.choices.every(isChoiceBody)) {
    return false
  }
  if (!isNullableString(value.chosen_choice_id) || !isNullableString(value.correct_choice_id)) return false
  if (value.correct !== undefined && value.correct !== null && typeof value.correct !== 'boolean') return false
  if (value.page !== undefined && value.page !== null && typeof value.page !== 'number') return false
  return true
}

export function isQuizDetailBody(value) {
  if (!isQuizCardBody(value)) return false
  if (value.status !== 'take' && value.status !== 'result') return false
  if (!Array.isArray(value.questions) || value.questions.length < 3 || value.questions.length > 8) {
    return false
  }
  if (!value.questions.every(isQuizQuestionBody)) return false
  if (value.status === 'take') return typeof value.current_index === 'number'
  return value.current_index === undefined || value.current_index === null || typeof value.current_index === 'number'
}

export function isSendResultBody(value) {
  if (
    !(
      isRecord(value) &&
      typeof value.chat_id === 'string' &&
      Array.isArray(value.lines) &&
      value.lines.every(isLineBody)
    )
  ) {
    return false
  }
  if (value.error === undefined || value.error === null) return true
  return (
    isRecord(value.error) &&
    typeof value.error.code === 'string' &&
    typeof value.error.message === 'string'
  )
}
