function isRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

const PROGRESS_BANDS = new Set(['mastered', 'medium', 'weak'])
const MATERIAL_KINDS = new Set(['pdf', 'presentation'])
const ACTIVITY_KINDS = new Set(['chat', 'quiz', 'examiner', 'presentation', 'document'])

function isProgressTopicNode(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    typeof value.mastery === 'number' &&
    value.mastery >= 0 &&
    value.mastery <= 100 &&
    typeof value.material_id === 'string' &&
    typeof value.band === 'string' &&
    PROGRESS_BANDS.has(value.band)
  )
}

function isProgressActivityItem(value) {
  return (
    isRecord(value) &&
    typeof value.at === 'string' &&
    typeof value.kind === 'string' &&
    ACTIVITY_KINDS.has(value.kind) &&
    typeof value.title === 'string'
  )
}

function isProgressMaterialChip(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    typeof value.kind === 'string' &&
    MATERIAL_KINDS.has(value.kind)
  )
}

export function isProgressBody(value) {
  return (
    isRecord(value) &&
    typeof value.average_mastery === 'number' &&
    value.average_mastery >= 0 &&
    value.average_mastery <= 100 &&
    typeof value.weak_topic_count === 'number' &&
    value.weak_topic_count >= 0 &&
    typeof value.sessions_this_week === 'number' &&
    value.sessions_this_week >= 0 &&
    value.sessions_this_week <= 7 &&
    typeof value.quizzes_finished === 'number' &&
    value.quizzes_finished >= 0 &&
    Array.isArray(value.topics) &&
    value.topics.every(isProgressTopicNode) &&
    Array.isArray(value.weak_topics) &&
    value.weak_topics.every(isProgressTopicNode) &&
    Array.isArray(value.activity) &&
    value.activity.length <= 50 &&
    value.activity.every(isProgressActivityItem) &&
    Array.isArray(value.materials) &&
    value.materials.every(isProgressMaterialChip)
  )
}
