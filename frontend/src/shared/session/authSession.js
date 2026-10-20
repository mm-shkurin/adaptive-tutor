import { browserStorage } from '../lib/browser'
import { notify, subscribe } from '../lib/listeners'

const STORAGE_KEY = 'adaptivetutor.session'

let current = null
let loaded = false
const listeners = new Set()

export function subscribeToSession(listener) {
  return subscribe(listeners, listener)
}

export function currentSession() {
  if (!loaded) {
    current = readStored()
    loaded = true
  }
  return current
}

export function isSignedIn() {
  return currentSession() !== null
}

export function startSession(session) {
  current = session
  loaded = true
  try {
    browserStorage()?.setItem(STORAGE_KEY, JSON.stringify(session))
  } catch {
    // Сессия останется в памяти вкладки.
  }
  notify(listeners)
}

export function renewTokens(accessToken, refreshToken) {
  const session = currentSession()
  if (!session) return
  startSession({ ...session, accessToken, refreshToken })
}

export function updateIdentity(displayName, avatarUrl, email) {
  const session = currentSession()
  if (!session) return
  const nextEmail = email === undefined ? (session.email ?? '') : email
  if (
    session.displayName === displayName &&
    session.avatarUrl === avatarUrl &&
    (session.email ?? '') === nextEmail
  ) {
    return
  }
  startSession({ ...session, displayName, avatarUrl, email: nextEmail })
}

export function endSession() {
  current = null
  loaded = true
  browserStorage()?.removeItem(STORAGE_KEY)
  notify(listeners)
}

function readStored() {
  const raw = browserStorage()?.getItem(STORAGE_KEY)
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw)
    return isSession(parsed) ? parsed : null
  } catch {
    return null
  }
}

function isSession(value) {
  if (typeof value !== 'object' || value === null) return false
  return (
    typeof value.accessToken === 'string' &&
    value.accessToken !== '' &&
    typeof value.refreshToken === 'string' &&
    typeof value.userId === 'string' &&
    typeof value.displayName === 'string' &&
    (value.avatarUrl === null || typeof value.avatarUrl === 'string') &&
    (value.email === undefined || typeof value.email === 'string')
  )
}
