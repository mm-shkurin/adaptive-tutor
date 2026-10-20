import { describe, expect, it } from 'vitest'
import { callbackOutcome, EXCHANGE_REFUSED, MALFORMED_CALLBACK } from './callbackOutcome'

describe('callbackOutcome', () => {
  it('exchanges a one-time code', () => {
    expect(callbackOutcome(new URLSearchParams('code=abc'))).toEqual({ kind: 'exchange', code: 'abc' })
  })

  it('refuses a provider failure without opening a session', () => {
    const outcome = callbackOutcome(new URLSearchParams('error=provider_failed'))
    expect(outcome.kind).toBe('refused')
    expect(outcome.reason).not.toMatch(/@|eyJ/)
  })

  it('treats a missing or huge code as a malformed return', () => {
    expect(callbackOutcome(new URLSearchParams('code=')).kind).toBe('malformed')
    expect(callbackOutcome(new URLSearchParams(`code=${'a'.repeat(513)}`)).kind).toBe('malformed')
    expect(MALFORMED_CALLBACK).not.toMatch(/@/)
    expect(EXCHANGE_REFUSED).not.toMatch(/@/)
  })
})
