const PERSON_ROLE = 'Вы'
const TUTOR_ROLE = 'AI-тьютор'
const SOURCES_TITLE = 'Источники'
const HEADING = 'Чат с AI-тьютором'
const EMPTY_THREAD = 'Пока нет сообщений'
const NO_READY = 'Нет готового PDF для чата.'
const NOTICE_DEFAULT = 'Материал пока нельзя спросить.'

export const MODES = [
  { id: 'professor', label: 'Профессор' },
  { id: 'five_year_old', label: 'Пятилетний' },
  { id: 'socratic', label: 'Сократический' },
  { id: 'examiner', label: 'Экзаменатор' },
]

export const MODELS = [
  'auto',
  'auto:smart',
  'auto:fast',
  'qwen/qwen3-32b',
  'meta-llama/llama-3.3-70b',
  'google/gemini-2.0-flash',
  'mistralai/mistral-small',
  'deepseek/deepseek-chat',
  'fusion',
]

export function pageCitation(page) {
  if (page == null) return null
  return `страница ${page}`
}

export function sourcePageLabel(page) {
  return pageCitation(page)
}

export function chatListRows(summaries) {
  return summaries.map((chat) => ({
    id: chat.id,
    documentName: chat.document_name,
    preview: chat.preview,
  }))
}

export function threadLines(lines) {
  return lines.map((line) => ({
    id: line.id,
    role: line.role,
    roleLabel: line.role === 'person' ? PERSON_ROLE : TUTOR_ROLE,
    cssRole: line.role === 'person' ? 'user' : 'agent',
    text: line.text,
    model: line.model ?? null,
    citation: line.role === 'tutor' ? pageCitation(line.page ?? null) : null,
    page: line.page ?? null,
  }))
}

export function sourcesFromLines(lines) {
  const tutor = [...lines].reverse().find((line) => line.role === 'tutor' && Array.isArray(line.sources))
  if (!tutor?.sources?.length) return []
  return tutor.sources.map((source, index) => ({
    key: `${tutor.id}-${index}`,
    pageLabel: sourcePageLabel(source.page ?? null),
    text: source.text,
  }))
}

export function chatScreenView({ summaries, chat, emptyReason }) {
  return {
    heading: HEADING,
    sourcesTitle: SOURCES_TITLE,
    emptyThread: EMPTY_THREAD,
    noReady: NO_READY,
    emptyReason: emptyReason ?? null,
    notice: chat && !chat.askable ? chat.notice || NOTICE_DEFAULT : null,
    documentName: chat?.document_name ?? null,
    askable: chat?.askable ?? false,
    rows: chatListRows(summaries ?? []),
    lines: threadLines(chat?.lines ?? []),
    sources: sourcesFromLines(chat?.lines ?? []),
  }
}
