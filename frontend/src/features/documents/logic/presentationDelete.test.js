import { describe, expect, it, vi } from 'vitest'
import { DELETE_PRESENTATION_PROMPT, presentationDeleteConfirmed } from './presentationDelete'

describe('presentationDelete', () => {
  it('presentationDeleteConfirmed follows window.confirm', () => {
    const confirm = vi.fn(() => true)
    expect(presentationDeleteConfirmed(confirm)).toBe(true)
    expect(confirm).toHaveBeenCalledWith(DELETE_PRESENTATION_PROMPT)
    expect(presentationDeleteConfirmed(vi.fn(() => false))).toBe(false)
    expect(presentationDeleteConfirmed(null, true)).toBe(true)
  })
})