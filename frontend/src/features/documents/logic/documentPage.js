export function pageWithUploaded(page, uploaded) {
  const rest = page.documents.filter((document) => document.id !== uploaded.id)
  return { documents: [uploaded, ...rest], has_next: page.has_next }
}

export function replaceDocuments(page, nextPage) {
  return nextPage
}

export function needsStatusPoll(documents) {
  return documents.some((document) => document.status === 'waiting' || document.status === 'indexing')
}
