import { readSuccessBody, toHttpError } from './httpResponse'

export { isHttpError } from './httpResponse'
import { REQUEST_TIMEOUT_MS, withTimeout } from './requestTimeout'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export async function request(path, options = {}) {
  return withTimeout((signal) => perform(path, options, signal), REQUEST_TIMEOUT_MS, options.signal)
}

async function perform(path, options, signal) {
  const response = await fetch(`${API_BASE}${path}`, buildInit(options, signal))
  if (!response.ok) throw await toHttpError(response)
  return readSuccessBody(response, options.guard)
}

function buildInit(options, signal) {
  const { method = 'GET', headers = {}, body } = options
  const binary = body instanceof FormData || body instanceof Blob
  return {
    method,
    signal,
    credentials: 'include',
    headers: body === undefined || binary ? headers : { 'Content-Type': 'application/json', ...headers },
    body: body === undefined ? undefined : binary ? body : JSON.stringify(body),
  }
}
