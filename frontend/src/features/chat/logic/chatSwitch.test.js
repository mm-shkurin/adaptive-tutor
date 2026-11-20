import { describe, expect, it } from 'vitest'
import { readyDocumentChoices } from './chatSwitch'

describe('readyDocumentChoices', () => {
  it('keeps only ready documents for new chat and switch choices', () => {
    const choices = readyDocumentChoices({
      documents: [
        { id: '1', name: 'ready.pdf', status: 'ready' },
        { id: '2', name: 'waiting.pdf', status: 'waiting' },
        { id: '3', name: 'indexing.pdf', status: 'indexing' },
        { id: '4', name: 'failed.pdf', status: 'failed' },
      ],
    })
    expect(choices).toEqual([{ id: '1', name: 'ready.pdf' }])
  })
})
