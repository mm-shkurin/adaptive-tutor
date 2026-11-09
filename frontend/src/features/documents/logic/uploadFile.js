import { failureText } from '../../../shared/api/failureText'
import { httpErrorIn } from '../../../shared/api/httpResponse'

export const MAX_PDF_BYTES = 52_428_800

export const NOT_A_PDF = 'Файл не PDF. Список не изменился.'
export const OVER_MAXIMUM = 'Файл больше 50 МБ. Список не изменился.'

const SERVER_REASON = {
  invalid_pdf: NOT_A_PDF,
  file_too_large: OVER_MAXIMUM,
}

export function uploadRefusal(file) {
  if (!isPdf(file)) return NOT_A_PDF
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
