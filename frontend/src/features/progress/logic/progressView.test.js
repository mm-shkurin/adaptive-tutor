import { describe, expect, it } from 'vitest'
import {
  bandDotClass,
  formatMasteryPercent,
  materialChips,
  progressView,
  weakTopicsOnly,
} from './progressView'

function topic(id, name, mastery, band) {
  return { id, name, mastery, material_id: 'mat-1', band }
}

function progressBody(overrides = {}) {
  return {
    average_mastery: 62,
    weak_topic_count: 1,
    sessions_this_week: 3,
    quizzes_finished: 4,
    topics: [
      topic('t1', 'Матрицы', 75, 'mastered'),
      topic('t2', 'Интегралы', 35, 'weak'),
    ],
    weak_topics: [topic('t2', 'Интегралы', 35, 'weak')],
    activity: [],
    materials: [{ id: 'mat-1', name: 'Линейная алгебра', kind: 'pdf' }],
    ...overrides,
  }
}

describe('progressView', () => {
  it('formats mastery and builds four stat tiles', () => {
    expect(formatMasteryPercent(61.6)).toBe('62%')
    const view = progressView(progressBody())
    expect(view.stats).toHaveLength(4)
    expect(view.stats.map((s) => s.testId)).toEqual([
      'prog-mastery',
      'prog-weak-n',
      'prog-sessions',
      'prog-quizzes',
    ])
    expect(view.stats[0].value).toBe('62%')
    expect(view.stats[1].value).toBe('1')
    expect(view.stats[2].value).toBe('3')
    expect(view.stats[3].value).toBe('4')
  })

  it('maps topic nodes and weak rows with band classes', () => {
    const view = progressView(progressBody())
    expect(view.topicNodes).toHaveLength(2)
    expect(view.topicNodes[0]).toMatchObject({
      name: 'Матрицы',
      masteryLabel: '75%',
      bandClass: 'prog-band-mastered',
    })
    expect(view.weakTopics).toHaveLength(1)
    expect(view.weakTopics[0].barWidth).toBe('35%')
    expect(bandDotClass('medium')).toBe('prog-band-medium')
    expect(bandDotClass('weak')).toBe('prog-band-weak')
  })

  it('marks the active material chip', () => {
    const chips = materialChips(progressBody().materials, 'mat-1')
    expect(chips[0]).toMatchObject({ label: 'Все материалы', active: false })
    expect(chips[1]).toMatchObject({ id: 'mat-1', active: true })
  })

  it('weak list keeps only topics below 40% and matches the weak count', () => {
    const view = progressView(
      progressBody({
        weak_topic_count: 2,
        weak_topics: [
          topic('t2', 'Интегралы', 35, 'weak'),
          topic('t3', 'Среднее', 52, 'medium'),
          topic('t4', 'Ещё слабо', 10, 'weak'),
        ],
      }),
    )
    expect(weakTopicsOnly(view.weakTopics).map((row) => row.name)).toEqual(['Интегралы', 'Ещё слабо'])
    expect(view.weakTopics).toHaveLength(2)
    expect(view.stats.find((stat) => stat.key === 'weak').value).toBe('2')
    expect(view.topicNodes[0].materialId).toBe('mat-1')
  })
})