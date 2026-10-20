export const REQUEST_TIMEOUT_MS = 15000

export class RequestTimeoutError extends Error {
  constructor(ms) {
    super(`Запрос не ответил за ${Math.round(ms / 1000)} с.`)
    this.name = 'RequestTimeoutError'
  }
}

export function isRequestTimeout(error) {
  return error instanceof RequestTimeoutError
}

export async function withTimeout(run, ms = REQUEST_TIMEOUT_MS, external) {
  const controller = new AbortController()
  const abortExternally = () => controller.abort()
  external?.addEventListener('abort', abortExternally)
  const timer = setTimeout(() => controller.abort(), ms)
  try {
    return await run(controller.signal)
  } catch (error) {
    if (controller.signal.aborted && !external?.aborted) throw new RequestTimeoutError(ms)
    throw error
  } finally {
    clearTimeout(timer)
    external?.removeEventListener('abort', abortExternally)
  }
}
