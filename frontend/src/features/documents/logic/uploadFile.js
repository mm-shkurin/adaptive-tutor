import { failureText } from '../../../shared/api/failureText'
import { httpErrorIn } from '../../../shared/api/httpResponse'

export const MIN_PDF_BYTES = 1_048_576
export const MAX_PDF_BYTES = 52_428_800

export const NOT_A_PDF = 'Файл не PDF. Список не изменился.'
export const UNDER_MINIMUM = 'Файл меньше 1 МБ. Список не изменился.'
export const OVER_MAXIMUM = 'Файл больше 50 МБ. Список не изменился.'
export const VIRUS_BLOCKED = 'Проверка не пропустила файл. Список не изменился.'
export const RATE_LIMITED = 'Слишком много загрузок за минуту. Список не изменился.'

const SERVER_REASON = {
  invalid_pdf: NOT_A_PDF,
  empty_pdf: NOT_A_PDF,
  file_too_small: UNDER_MINIMUM,
  file_too_large: OVER_MAXIMUM,
  virus_detected: VIRUS_BLOCKED,
  rate_limited: RATE_LIMITED,
  rate_unavailable: RATE_LIMITED,
}

export function uploadRefusal(file) {
  if (!isPdf(file)) return NOT_A_PDF
  if (file.size < MIN_PDF_BYTES) return UNDER_MINIMUM
  if (file.size > MAX_PDF_BYTES) return OVER_MAXIMUM
  return null
}

export function uploadErrorMessage(error) {
  const failure = httpErrorIn(error)
  if (failure?.errorCode && SERVER_REASON[failure.errorCode]) return SERVER_REASON[failure.errorCode]
  return failureText(error)
}

export function presentationDoorResult() {
  return { startsPdfUpload: false }
}

function isPdf(file) {
  if (file?.type === 'application/pdf') return true
  return typeof file?.name === 'string' && file.name.toLowerCase().endsWith('.pdf')
}
