import { afterEach, describe, expect, it } from 'vitest'
import { initTheme, setTheme, THEME_STORAGE_KEY, themeChoice } from './themeStore'

afterEach(() => {
  localStorage.clear()
  document.documentElement.removeAttribute('data-theme')
})

describe('themeStore', () => {
  it('paints a saved choice before the screen and keeps it on this device', () => {
    setTheme('dark')
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
    expect(THEME_STORAGE_KEY).not.toBe('absolute.theme')
  })

  it('paints the system theme for an unknown value', () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'blue')
    initTheme()
    expect(themeChoice()).toBe('system')
    expect(document.documentElement.hasAttribute('data-theme')).toBe(false)
  })
})
