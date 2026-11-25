export function readyPdfMaterials(documents) {
  if (!Array.isArray(documents)) return []
  return documents.filter((document) => document.kind === 'pdf' && document.status === 'ready')
}

export function parsePdfPageList(raw, pageCount) {
  if (typeof raw !== 'string' || raw.trim() === '') return []
  const seen = new Set()
  const pages = []
  for (const part of raw.split(/[,;\s]+/)) {
    if (part === '') continue
    const value = Number(part)
    if (!Number.isInteger(value) || value < 1) continue
    if (pageCount != null && value > pageCount) continue
    if (seen.has(value)) continue
    seen.add(value)
    pages.push(value)
  }
  return pages
}