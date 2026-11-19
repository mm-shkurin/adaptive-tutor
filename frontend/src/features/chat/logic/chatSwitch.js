export function readyDocumentChoices(page) {
  return (page.documents ?? [])
    .filter((doc) => doc.status === 'ready')
    .map((doc) => ({ id: doc.id, name: doc.name }))
}

export function upsertSummary(rows, chat) {
  const row = {
    id: chat.id,
    document_id: chat.document_id,
    document_name: chat.document_name,
    preview: rows.find((item) => item.id === chat.id)?.preview ?? null,
  }
  const without = rows.filter((item) => item.id !== chat.id)
  return [row, ...without]
}

export function summaryFromChat(chat) {
  return {
    id: chat.id,
    document_id: chat.document_id,
    document_name: chat.document_name,
    preview: null,
  }
}
