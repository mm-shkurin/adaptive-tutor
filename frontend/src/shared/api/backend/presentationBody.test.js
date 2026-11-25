import { describe, expect, it } from 'vitest'
import { isPresentationBody } from './bodyGuards'

describe('presentation body guards', () => {
  it('accepts an empty draft from create', () => {
    expect(
      isPresentationBody({
        id: 'pres-1',
        title: 'Новая презентация',
        status: 'draft',
        slide_count: 0,
        piece_count: null,
        error: null,
        slides: [],
      }),
    ).toBe(true)
  })

  it('rejects a missing slide_count', () => {
    expect(
      isPresentationBody({
        id: 'pres-1',
        title: 'Новая презентация',
        status: 'draft',
        piece_count: null,
        error: null,
        slides: [],
      }),
    ).toBe(false)
  })
})