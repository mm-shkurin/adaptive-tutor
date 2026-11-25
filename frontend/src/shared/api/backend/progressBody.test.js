import { describe, expect, it } from 'vitest'
import { isProgressBody } from './bodyGuards'

function topic(overrides = {}) {
  return {
    id: 'topic-1',
    name: 'Производные',
    mastery: 55,
    material_id: '11111111-1111-4111-8111-111111111111',
    band: 'medium',
    ...overrides,
  }
}

function body(overrides = {}) {
  return {
    average_mastery: 50,
    weak_topic_count: 0,
    sessions_this_week: 2,
    quizzes_finished: 1,
    topics: [topic()],
    weak_topics: [],
    activity: [{ at: '2026-11-25T12:00:00Z', kind: 'quiz', title: 'Викторина' }],
    materials: [{ id: '11111111-1111-4111-8111-111111111111', name: 'Курс', kind: 'pdf' }],
    ...overrides,
  }
}

describe('isProgressBody', () => {
  it('accepts a full progress payload', () => {
    expect(isProgressBody(body())).toBe(true)
    expect(isProgressBody(body({ weak_topics: [topic({ mastery: 20, band: 'weak' })] }))).toBe(true)
  })

  it('rejects out-of-range stats and unknown bands', () => {
    expect(isProgressBody(body({ sessions_this_week: 8 }))).toBe(false)
    expect(isProgressBody(body({ topics: [topic({ band: 'unknown' })] }))).toBe(false)
    expect(isProgressBody(body({ activity: [{ at: 'x', kind: 'nope', title: 't' }] }))).toBe(false)
  })
})