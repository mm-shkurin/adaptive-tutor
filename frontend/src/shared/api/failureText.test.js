import { describe, expect, it } from 'vitest'
import { failureText } from './failureText'
import { RequestTimeoutError } from './requestTimeout'

describe('failureText', () => {
  it('does not repeat a token or an email from the server', () => {
    const error = new Error('token eyJabc ada@yandex.ru')
    error.status = 400
    error.errorCode = 'unauthorized'
    expect(failureText(error)).not.toMatch(/@|eyJ/)
  })

  it('names a refused name and a late server', () => {
    const refused = new Error('Name is not allowed')
    refused.status = 422
    refused.errorCode = 'invalid_name'
    expect(failureText(refused)).toMatch(/60/)
    const wrapped = new Error('wrapped', { cause: new RequestTimeoutError(15000) })
    expect(failureText(wrapped)).toMatch(/не ответил/)
  })
})
