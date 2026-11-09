const EMPTY_LIST = 'Пока нет материалов'

const LIBRARY_COPY = {
  heading: 'Документы',
  pdfDoor: {
    title: 'Загрузить PDF',
    hint: 'до 50 MB · парсинг и индексация',
  },
  presentationDoor: 'Создать презентацию',
}

const STATUS = {
  waiting: { label: 'Ждёт', pill: 'waiting' },
  indexing: { label: 'В процессе', pill: 'processing' },
  ready: { label: 'Готов', pill: 'ready' },
  failed: { label: 'Не удалось', pill: 'failed' },
}

export function libraryView(page) {
  return {
    ...LIBRARY_COPY,
    emptyList: emptyListMessage(page.documents),
    rows: page.documents.map(documentRow),
  }
}

function emptyListMessage(documents) {
  return documents.length === 0 ? EMPTY_LIST : null
}

function documentRow(document) {
  const status = STATUS[document.status]
  return {
    id: document.id,
    name: document.name,
    meta: documentMeta(document),
    statusLabel: status.label,
    statusPill: status.pill,
    failureReason: document.status === 'failed' ? document.error : null,
  }
}

function documentMeta(document) {
  if (document.status === 'failed' && document.error) return document.error
  const size = formatMegabytes(document.size_bytes)
  switch (document.status) {
    case 'waiting':
      return `${size} · ждёт индексации`
    case 'indexing':
      return indexingMeta(size, document.page_count)
    case 'ready':
      return `${size} · ${document.page_count} стр. · ${document.piece_count} чанков`
    default:
      return size
  }
}

function indexingMeta(size, pageCount) {
  const pages = pageCount == null ? '' : `${pageCount} стр. · `
  return `${size} · ${pages}индексация…`
}

function formatMegabytes(sizeBytes) {
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`
}
