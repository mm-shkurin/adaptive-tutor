import { describe, expect, it } from 'vitest'
import { VIRUS_SCAN_BUDGET_MS } from '../../../features/documents/logic/statusStreamPolicy'
import { UPLOAD_TIMEOUT_MS } from './documentApi'

describe('documentApi upload budget', () => {
  it('UPLOAD_TIMEOUT_MS outlasts the server virus-scan budget', () => {
    expect(UPLOAD_TIMEOUT_MS).toBeGreaterThanOrEqual(VIRUS_SCAN_BUDGET_MS)
  })

  it('UPLOAD_TIMEOUT_MS keeps headroom beyond the 30s virus budget for transfer', () => {
    expect(UPLOAD_TIMEOUT_MS).toBeGreaterThanOrEqual(90_000)
  })
})
