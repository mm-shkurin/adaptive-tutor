import { describe, expect, it } from 'vitest'
import { SessionExpiredError } from '../../session/authorizedRequest'
import {
  isStreamOpenError,
  resolveDocumentStatusStreamBase,
} from './documentStatusStream'

describe('documentStatusStream', () => {
  it('resolveDocumentStatusStreamBase prefers SSE base, then proxy target, then API base', () => {
    expect(
      resolveDocumentStatusStreamBase({
        VITE_SSE_BASE_URL: 'http://sse.test',
        VITE_API_PROXY_TARGET: 'http://proxy.test',
        VITE_API_BASE_URL: 'http://api.test',
      }),
    ).toBe('http://sse.test')
    expect(
      resolveDocumentStatusStreamBase({
        VITE_API_PROXY_TARGET: 'http://127.0.0.1:8010',
        VITE_API_BASE_URL: 'http://api.test',
      }),
    ).toBe('http://127.0.0.1:8010')
    expect(resolveDocumentStatusStreamBase({ VITE_API_BASE_URL: 'http://api.test' })).toBe(
      'http://api.test',
    )
    expect(resolveDocumentStatusStreamBase({})).toBe('')
  })

  it('isStreamOpenError ignores AbortError and session expiry', () => {
    expect(isStreamOpenError(new SessionExpiredError())).toBe(false)
    const abort = new Error('aborted')
    abort.name = 'AbortError'
    expect(isStreamOpenError(abort)).toBe(false)
  })

  it('isStreamOpenError treats HTTP 4xx/5xx and TypeError as stream-open failures', () => {
    const httpError = new Error('gone')
    httpError.name = 'HttpError'
    httpError.status = 503
    expect(isStreamOpenError(httpError)).toBe(true)
    expect(isStreamOpenError(new TypeError('Failed to fetch'))).toBe(true)
    expect(isStreamOpenError(new Error('parse failed'))).toBe(false)
  })
})
