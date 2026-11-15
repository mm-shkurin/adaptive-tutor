function isRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

export function isTokenPairBody(value) {
  return isRecord(value) && typeof value.access_token === 'string' && typeof value.refresh_token === 'string'
}

export function isProfileBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    typeof value.email === 'string' &&
    typeof value.created_at === 'string' &&
    (value.avatar_url === null || typeof value.avatar_url === 'string')
  )
}

const DOCUMENT_STATUSES = new Set(['waiting', 'indexing', 'ready', 'failed'])

export function isDocumentBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    typeof value.size_bytes === 'number' &&
    (value.page_count === null || typeof value.page_count === 'number') &&
    (value.piece_count === null || typeof value.piece_count === 'number') &&
    DOCUMENT_STATUSES.has(value.status) &&
    (value.error === null || typeof value.error === 'string')
  )
}

export function isDocumentPageBody(value) {
  return (
    isRecord(value) &&
    Array.isArray(value.documents) &&
    value.documents.every(isDocumentBody) &&
    typeof value.has_next === 'boolean'
  )
}

export function isChatSummaryBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.document_id === 'string' &&
    typeof value.document_name === 'string' &&
    (value.preview === null || typeof value.preview === 'string')
  )
}

export function isChatListBody(value) {
  return isRecord(value) && Array.isArray(value.chats) && value.chats.every(isChatSummaryBody)
}

export function isSourceBody(value) {
  return (
    isRecord(value) &&
    typeof value.text === 'string' &&
    (value.page === null || value.page === undefined || typeof value.page === 'number')
  )
}

export function isLineBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    (value.role === 'person' || value.role === 'tutor') &&
    typeof value.text === 'string'
  )
}

export function isChatBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.document_id === 'string' &&
    typeof value.document_name === 'string' &&
    typeof value.askable === 'boolean' &&
    (value.notice === null || typeof value.notice === 'string') &&
    Array.isArray(value.lines) &&
    value.lines.every(isLineBody)
  )
}

export function isSendResultBody(value) {
  return (
    isRecord(value) &&
    typeof value.chat_id === 'string' &&
    Array.isArray(value.lines) &&
    value.lines.every(isLineBody)
  )
}
