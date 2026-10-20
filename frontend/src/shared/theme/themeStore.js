import { browserDocument, browserStorage } from '../lib/browser'
import { notify, subscribe } from '../lib/listeners'

export const THEME_STORAGE_KEY = 'adaptivetutor.theme'

const listeners = new Set()

export function subscribeToTheme(listener) {
  return subscribe(listeners, listener)
}

export function themeChoice() {
  const saved = browserStorage()?.getItem(THEME_STORAGE_KEY)
  return saved === 'dark' || saved === 'light' ? saved : 'system'
}

export function setTheme(choice) {
  try {
    if (choice === 'system') browserStorage()?.removeItem(THEME_STORAGE_KEY)
    else browserStorage()?.setItem(THEME_STORAGE_KEY, choice)
  } catch {
    // Тема продержится до перезагрузки.
  }
  applyChoice(choice)
  notify(listeners)
}

export function initTheme() {
  applyChoice(themeChoice())
}

export function themeMenuLabel(choice = themeChoice()) {
  return painted(choice) === 'dark' ? 'тёмная' : 'светлая'
}

export function flipTheme(choice = themeChoice()) {
  setTheme(painted(choice) === 'dark' ? 'light' : 'dark')
}

function applyChoice(choice) {
  const root = browserDocument()?.documentElement
  if (!root) return
  if (choice === 'system') root.removeAttribute('data-theme')
  else root.setAttribute('data-theme', choice)
}

function painted(choice) {
  if (choice === 'dark' || choice === 'light') return choice
  return prefersDark() ? 'dark' : 'light'
}

function prefersDark() {
  return browserDocument()?.defaultView?.matchMedia('(prefers-color-scheme: dark)').matches ?? false
}
