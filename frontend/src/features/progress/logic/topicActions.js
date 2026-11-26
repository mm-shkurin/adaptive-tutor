export function quizCreateTarget(topic) {
  if (!topic?.materialId || !topic?.name) return null
  return {
    path: '/quizzes/new',
    state: { documentId: topic.materialId, topic: topic.name },
  }
}

export function chatForMaterialTarget(topic) {
  if (!topic?.materialId) return null
  return {
    path: '/chat',
    state: { documentId: topic.materialId },
  }
}
