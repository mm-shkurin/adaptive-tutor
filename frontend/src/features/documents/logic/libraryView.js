const EMPTY_LIST = 'Пока нет материалов'

const STATUS_LABEL = {
  waiting: 'Ждёт',
  indexing: 'В процессе',
  ready: 'Готов',
  failed: 'Не удалось',
}

const STATUS_PILL = {
  waiting: 'waiting',
  indexing: 'processing',
  ready: 'ready',
  failed: 'failed',
}

export function libraryView(page) {
  const emptyList = page.documents.length === 0 ? EMPTY_LIST : null
  return {
    heading: 'Документы',
    pdfDoor: {
      title: 'Загрузить PDF',
      hint: 'до 50 MB · парсинг и индексация',
    },
    presentationDoor: 'Создать презентацию',
    emptyList,
    rows: page.documents.map(documentRow),
  }
}

function documentRow(document) {
  return {
    id: document.id,
    name: document.name,
    meta: documentMeta(document),
    statusLabel: STATUS_LABEL[document.status],
    statusPill: STATUS_PILL[document.status],
    failureReason: document.status === 'failed' ? document.error : null,
  }
}

function documentMeta(document) {
  const size = formatMegabytes(document.size_bytes)
  if (document.status === 'waiting') return `${size} · ждёт индексации`
  if (document.status === 'indexing') {
    const pages = document.page_count == null ? '' : `${document.page_count} стр. · `
    return `${size} · ${pages}индексация…`
  }
  if (document.status === 'ready') {
    return `${size} · ${document.page_count} стр. · ${document.piece_count} чанков`
  }
  return size
}

function formatMegabytes(sizeBytes) {
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`
}
