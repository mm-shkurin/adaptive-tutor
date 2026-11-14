import { describe, expect, it } from 'vitest'
import { FALLBACK_POLL_LIMIT, FALLBACK_POLL_MS, VIRUS_SCAN_BUDGET_MS } from './statusStreamPolicy'

describe('statusStreamPolicy', () => {
  it('caps SSE fallback list polls instead of polling forever', () => {
    expect(FALLBACK_POLL_MS).toBe(1000)
    expect(FALLBACK_POLL_LIMIT).toBeGreaterThan(0)
    expect(FALLBACK_POLL_LIMIT).toBeLessThanOrEqual(60)
  })

  it('names the virus-scan budget the upload client must cover', () => {
    expect(VIRUS_SCAN_BUDGET_MS).toBe(30_000)
  })
})
