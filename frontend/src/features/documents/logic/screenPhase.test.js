import { describe, expect, it } from 'vitest'
import { screenPhase } from './screenPhase'

const EMPTY_LIBRARY = 'Пока нет материалов'

describe('screenPhase', () => {
  it('A list that is loading or that failed to load is not the empty library', () => {
    const loading = screenPhase('loading')
    const failed = screenPhase('error')
    expect(loading.error).toBeNull()
    expect(loading.retry).toBeNull()
    expect(JSON.stringify(loading)).not.toContain(EMPTY_LIBRARY)
    expect(failed.error).toBe('Не удалось открыть документы.')
    expect(failed.retry).toBe('Повторить')
    expect(failed.error).not.toContain(EMPTY_LIBRARY)
  })
})
