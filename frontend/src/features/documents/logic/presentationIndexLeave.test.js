import { describe, expect, it } from 'vitest'
import { leaveEditorAfterIndex } from './presentationIndexLeave'

describe('presentationIndexLeave', () => {
  it('leaves the editor when index returns ready so Documents can show the row', () => {
    expect(leaveEditorAfterIndex('ready')).toBe(true)
  })

  it('keeps the editor open when index did not reach ready', () => {
    expect(leaveEditorAfterIndex('draft')).toBe(false)
    expect(leaveEditorAfterIndex('indexing')).toBe(false)
    expect(leaveEditorAfterIndex('failed')).toBe(false)
  })
})
