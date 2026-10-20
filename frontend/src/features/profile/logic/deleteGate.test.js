import { describe, expect, it } from 'vitest'
import { canDeleteAccount } from './deleteGate'

describe('canDeleteAccount', () => {
  it('stays off until the typed email equals the account email', () => {
    expect(canDeleteAccount('ada@yandex.ru', 'ada@yandex.ru')).toBe(true)
    expect(canDeleteAccount('ada@yandex.com', 'ada@yandex.ru')).toBe(false)
    expect(canDeleteAccount('', 'ada@yandex.ru')).toBe(false)
    expect(canDeleteAccount('ada@yandex.ru', '')).toBe(false)
  })
})
