import { describe, expect, it } from 'vitest'
import { applySendLines, mergeLines, shouldPaintSend } from './sendResult'

describe('sendResult', () => {
  it('does not paint a late reply onto another open chat', () => {
    expect(shouldPaintSend('open-chat', 'left-chat')).toBe(false)
    const kept = [{ id: 'a', text: 'shown' }]
    expect(applySendLines(kept, [{ id: 'late', text: 'left reply' }], 'open-chat', 'left-chat')).toEqual(
      kept,
    )
  })

  it('keeps a later response when an earlier one arrives after it', () => {
    const later = [
      { id: 'p2', role: 'person', text: 'later Q' },
      { id: 't2', role: 'tutor', text: 'later A' },
    ]
    const earlier = [
      { id: 'p1', role: 'person', text: 'earlier Q' },
      { id: 't1', role: 'tutor', text: 'earlier A' },
    ]
    const afterLater = applySendLines([], later, 'chat', 'chat')
    const afterBoth = applySendLines(afterLater, earlier, 'chat', 'chat')
    expect(afterBoth.map((line) => line.id)).toEqual(['p2', 't2', 'p1', 't1'])
    expect(afterBoth.find((line) => line.id === 't2').text).toBe('later A')
  })

  it('merges without dropping existing tutor lines', () => {
    const existing = [{ id: 'keep', text: 'later A' }]
    expect(mergeLines(existing, [{ id: 'add', text: 'earlier A' }])).toEqual([
      { id: 'keep', text: 'later A' },
      { id: 'add', text: 'earlier A' },
    ])
  })
})
