const STATUS_RANK = { waiting: 0, indexing: 1, ready: 2, failed: 2 }

export function pageWithUploaded(page, uploaded) {
  const rest = page.documents.filter((document) => document.id !== uploaded.id)
  return { documents: [uploaded, ...rest], has_next: page.has_next }
}

export function needsStatusStream(documents) {
  return documents.some((document) => document.status === 'waiting' || document.status === 'indexing')
}

export function pageWithStatusEvent(page, update) {
  if (!page) return page
  const matched = page.documents.some((document) => document.id === update.id)
  if (!matched) {
    return { documents: [update, ...page.documents], has_next: page.has_next }
  }
  return {
    documents: page.documents.map((document) =>
      document.id === update.id ? keepNewerStatus(document, { ...document, ...update }) : document
    ),
    has_next: page.has_next,
  }
}

export function fresherPage(current, incoming) {
  if (!current) return incoming
  const shown = new Map(current.documents.map((document) => [document.id, document]))
  const incomingIds = new Set(incoming.documents.map((document) => document.id))
  // A just-accepted upload can sit in current before the next list response includes it.
  // Keep those in-flight rows; do not let a slightly older list wipe them.
  const pending = current.documents.filter(
    (document) =>
      !incomingIds.has(document.id) &&
      (document.status === 'waiting' || document.status === 'indexing')
  )
  return {
    documents: [
      ...pending,
      ...incoming.documents.map((document) => keepNewerStatus(shown.get(document.id), document)),
    ],
    has_next: incoming.has_next,
  }
}

export function createListEpoch() {
  let current = 0
  return {
    start() {
      current += 1
      return current
    },
    accepts(requestId) {
      return requestId === current
    },
  }
}

export function createSubmission() {
  let pending = false
  return {
    begin(key) {
      if (pending) return null
      pending = true
      return key
    },
    finish() {
      pending = false
    },
  }
}

export function shouldApplyUpload(aborted) {
  return !aborted
}

function keepNewerStatus(shown, incoming) {
  if (!shown) return incoming
  if (statusRank(incoming.status) < statusRank(shown.status)) return shown
  return incoming
}

function statusRank(status) {
  return STATUS_RANK[status] ?? -1
}
