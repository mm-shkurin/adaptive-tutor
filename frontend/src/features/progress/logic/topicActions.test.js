import { describe, expect, it } from 'vitest'
import { chatForMaterialTarget, quizCreateTarget } from './topicActions'

const topic = { id: 'mat-1:Matrices', name: 'Matrices', materialId: 'mat-1', mastery: 35 }

describe('topicActions', () => {
  it('quizCreateTarget opens create with topic and material', () => {
    expect(quizCreateTarget(topic)).toEqual({
      path: '/quizzes/new',
      state: { documentId: 'mat-1', topic: 'Matrices' },
    })
  })

  it('chatForMaterialTarget opens chat for the material', () => {
    expect(chatForMaterialTarget(topic)).toEqual({
      path: '/chat',
      state: { documentId: 'mat-1' },
    })
  })

  it('refuses incomplete topics', () => {
    expect(quizCreateTarget({ name: 'x' })).toBeNull()
    expect(chatForMaterialTarget({ name: 'x' })).toBeNull()
  })
})
