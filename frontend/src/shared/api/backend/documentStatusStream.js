import { isDocumentBody } from './bodyGuards'
import { BACKEND } from './paths'
import { currentSession, endSession, renewTokens } from '../../session/authSession'
import { SessionExpiredError } from '../../session/authorizedRequest'
import { refreshTokens } from '../../session/refreshApi'
import { isHttpError, toHttpError } from '../httpResponse'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export async function openDocumentStatusStream({ signal, onEvent }) {
  const session = currentSession()
  if (!session) throw new SessionExpiredError()
  let response = await fetchStream(session.accessToken, signal)
  if (response.status === 401) {
    const renewed = await renewAccess()
    if (!renewed) {
      endSession()
      throw new SessionExpiredError()
    }
    response = await fetchStream(renewed, signal)
  }
  if (!response.ok) throw await toHttpError(response)
  await readEvents(response, signal, onEvent)
}

async function fetchStream(accessToken, signal) {
  return fetch(`${API_BASE}${BACKEND.documents.statusEvents}`, {
    method: 'GET',
    signal,
    credentials: 'include',
    headers: { Authorization: `Bearer ${accessToken}`, Accept: 'text/event-stream' },
  })
}

async function renewAccess() {
  const session = currentSession()
  if (!session) return null
  try {
    const pair = await refreshTokens(session.refreshToken)
    renewTokens(pair.accessToken, pair.refreshToken)
    return pair.accessToken
  } catch {
    return null
  }
}

async function readEvents(response, signal, onEvent) {
  if (!response.body) throw new Error('Document status stream has no body')
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (!signal?.aborted) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''
    for (const part of parts) {
      const document = parseDocumentEvent(part)
      if (document) onEvent(document)
    }
  }
}

function parseDocumentEvent(block) {
  let eventName = 'message'
  const dataLines = []
  for (const raw of block.split('\n')) {
    const line = raw.replace(/\r$/, '')
    if (!line || line.startsWith(':')) continue
    if (line.startsWith('event:')) {
      eventName = line.slice(6).trim()
      continue
    }
    if (line.startsWith('data:')) dataLines.push(line.slice(5).trimStart())
  }
  if (eventName !== 'document-status' || dataLines.length === 0) return null
  try {
    const payload = JSON.parse(dataLines.join('\n'))
    return isDocumentBody(payload) ? payload : null
  } catch {
    return null
  }
}

export function isStreamOpenError(error) {
  if (error instanceof SessionExpiredError) return false
  if (isHttpError(error)) return error.status >= 400
  return error instanceof TypeError || error instanceof Error
}
