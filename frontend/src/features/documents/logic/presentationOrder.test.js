import { describe, expect, it } from 'vitest'
import { moveSlide } from './presentationOrder'

const slides = [{ id: 'a' }, { id: 'b' }, { id: 'c' }]

describe('presentationOrder', () => {
  it('moves a slide up and down', () => {
    expect(moveSlide(slides, 'b', 'up')).toEqual(['b', 'a', 'c'])
    expect(moveSlide(slides, 'b', 'down')).toEqual(['a', 'c', 'b'])
  })

  it('returns null at the edges', () => {
    expect(moveSlide(slides, 'a', 'up')).toBeNull()
    expect(moveSlide(slides, 'c', 'down')).toBeNull()
  })
})
