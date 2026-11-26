function isRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isNullableString(value) {
  return value === undefined || value === null || typeof value === 'string'
}

const PRESENTATION_STATUSES = new Set(['draft', 'waiting', 'indexing', 'ready', 'failed'])
const SLIDE_SOURCES = new Set(['image', 'pdf_page', 'pptx', 'docx'])

function isSlideBody(value) {
  if (
    !(
      isRecord(value) &&
      typeof value.id === 'string' &&
      typeof value.position === 'number' &&
      value.position >= 1 &&
      typeof value.source === 'string' &&
      SLIDE_SOURCES.has(value.source) &&
      typeof value.text === 'string' &&
      typeof value.empty === 'boolean'
    )
  ) {
    return false
  }
  if (!isNullableString(value.formula_phrase) || !isNullableString(value.formula_latex)) return false
  if (
    value.pdf_document_id !== undefined &&
    value.pdf_document_id !== null &&
    typeof value.pdf_document_id !== 'string'
  ) {
    return false
  }
  if (value.pdf_page !== undefined && value.pdf_page !== null && typeof value.pdf_page !== 'number') {
    return false
  }
  return true
}

export function isPresentationBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.title === 'string' &&
    typeof value.status === 'string' &&
    PRESENTATION_STATUSES.has(value.status) &&
    typeof value.slide_count === 'number' &&
    value.slide_count >= 0 &&
    value.slide_count <= 40 &&
    Array.isArray(value.slides) &&
    value.slides.length <= 40 &&
    value.slides.every(isSlideBody) &&
    (value.piece_count === null || value.piece_count === undefined || typeof value.piece_count === 'number') &&
    (value.error === null || typeof value.error === 'string')
  )
}
