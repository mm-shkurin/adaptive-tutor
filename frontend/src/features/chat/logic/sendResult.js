export function mergeLines(existing, incoming) {
  const byId = new Map(existing.map((line) => [line.id, line]))
  for (const line of incoming) {
    byId.set(line.id, line)
  }
  const order = existing.map((line) => line.id)
  for (const line of incoming) {
    if (!order.includes(line.id)) order.push(line.id)
  }
  return order.map((id) => byId.get(id))
}

export function shouldPaintSend(activeChatId, sentChatId) {
  return activeChatId === sentChatId
}

export function applySendLines(currentLines, incoming, activeChatId, sentChatId) {
  if (!shouldPaintSend(activeChatId, sentChatId)) return currentLines
  return mergeLines(currentLines ?? [], incoming)
}
