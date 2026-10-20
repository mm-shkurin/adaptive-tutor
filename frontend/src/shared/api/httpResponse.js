export class UnexpectedBodyError extends Error {
  constructor(body) {
    super('Сервер вернул ответ неожиданной формы')
    this.name = 'UnexpectedBodyError'
    this.body = body
  }
}

export function isHttpError(error) {
  return httpErrorIn(error) !== null
}

export function httpErrorIn(error) {
  let step = error
  for (let depth = 0; step instanceof Error && depth < 5; depth += 1) {
    if (typeof step.status === 'number') return step
    step = step.cause
  }
  return null
}

export async function toHttpError(response) {
  const body = await readErrorBody(response)
  const error = new Error(body?.message ?? `HTTP ${response.status}`)
  error.name = 'HttpError'
  error.status = response.status
  error.errorCode = body?.code
  return error
}

async function readErrorBody(response) {
  try {
    const raw = await response.json()
    if (typeof raw !== 'object' || raw === null || Array.isArray(raw)) return undefined
    return {
      code: typeof raw.code === 'string' ? raw.code : undefined,
      message: typeof raw.message === 'string' ? raw.message : undefined,
    }
  } catch {
    return undefined
  }
}

export async function readSuccessBody(response, guard) {
  if (response.status === 204) return undefined
  const body = await response.json()
  if (guard && !guard(body)) throw new UnexpectedBodyError(body)
  return body
}
