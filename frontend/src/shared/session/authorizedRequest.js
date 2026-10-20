import { isHttpError, request } from '../api/httpClient'
import { currentSession, endSession, renewTokens } from './authSession'
import { refreshTokens } from './refreshApi'

export class SessionExpiredError extends Error {
  constructor() {
    super('Сессия истекла. Войдите заново.')
    this.name = 'SessionExpiredError'
  }
}

export function isSessionExpired(error) {
  return error instanceof SessionExpiredError
}

let inFlight = null

export async function authorizedRequest(path, options = {}) {
  const session = currentSession()
  if (!session) throw new SessionExpiredError()
  try {
    return await request(path, withToken(options, session.accessToken))
  } catch (error) {
    if (!isUnauthorized(error)) throw error
    if (!(await renewOnce())) {
      endSession()
      throw new SessionExpiredError()
    }
    const renewed = currentSession()
    if (!renewed) throw new SessionExpiredError()
    return request(path, withToken(options, renewed.accessToken))
  }
}

function withToken(options, token) {
  return { ...options, headers: { ...options.headers, Authorization: `Bearer ${token}` } }
}

function isUnauthorized(error) {
  return isHttpError(error) && error.status === 401
}

async function renewOnce() {
  inFlight ??= performRenewal().finally(() => {
    inFlight = null
  })
  return inFlight
}

async function performRenewal() {
  const session = currentSession()
  if (!session) return false
  try {
    const pair = await refreshTokens(session.refreshToken)
    renewTokens(pair.accessToken, pair.refreshToken)
    return true
  } catch {
    return false
  }
}
