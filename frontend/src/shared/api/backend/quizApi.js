import { send } from '../send'
import { isQuizDetailBody, isQuizListBody } from './bodyGuards'
import { BACKEND } from './paths'

/** Create waits on retrieval plus one freellmapi call, same budget as a chat send. */
export const CREATE_QUIZ_TIMEOUT_MS = 90_000

export function listQuizzes(signal) {
  return send(BACKEND.quizzes.list, { signal, guard: isQuizListBody })
}

export function getQuiz(id, signal) {
  return send(BACKEND.quizzes.item(id), { signal, guard: isQuizDetailBody })
}

export function createQuiz(body, idempotencyKey, signal) {
  return send(BACKEND.quizzes.list, {
    method: 'POST',
    body,
    headers: { 'Idempotency-Key': idempotencyKey },
    signal,
    timeoutMs: CREATE_QUIZ_TIMEOUT_MS,
    guard: isQuizDetailBody,
  })
}

export function answerQuiz(id, choiceId, signal) {
  return send(BACKEND.quizzes.answers(id), {
    method: 'POST',
    body: { choice_id: choiceId },
    signal,
    guard: isQuizDetailBody,
  })
}

export function advanceQuiz(id, signal) {
  return send(BACKEND.quizzes.advance(id), {
    method: 'POST',
    signal,
    guard: isQuizDetailBody,
  })
}

export function retryQuiz(id, signal) {
  return send(BACKEND.quizzes.retries(id), {
    method: 'POST',
    signal,
    guard: isQuizDetailBody,
  })
}
