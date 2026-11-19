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
  const open = openExaminerQuestion(lines)
  return lines.map((line) => ({
    id: line.id,
    role: line.role,
    roleLabel: line.role === 'person' ? PERSON_ROLE : TUTOR_ROLE,
    cssRole: line.role === 'person' ? 'user' : 'agent',
    text: line.text,
    model: line.model ?? null,
    kind: line.kind ?? null,
    citation: line.role === 'tutor' ? pageCitation(line.page ?? null) : null,
    page: line.page ?? null,
    choices: open && line.id === open.id ? line.choices ?? [] : [],
    gradeLabel: gradeLabel(line),
    choiceId: line.choice_id ?? null,
    correct: line.correct ?? null,
  }))
}

export function gradeLabel(line) {
  if (line?.kind !== 'grade') return null
  if (line.correct === true) return 'Верно'
  if (line.correct === false) return 'Неверно'
  return null
}

export function isWithholding(lines) {
  for (let index = lines.length - 1; index >= 0; index -= 1) {
    if (lines[index].role === 'tutor') return lines[index].kind === 'withheld'
  }
  return false
}

export function openExaminerQuestion(lines) {
  for (let index = lines.length - 1; index >= 0; index -= 1) {
    const line = lines[index]
    if (line.role !== 'tutor') continue
    if (line.kind === 'question') return line
    if (line.kind === 'grade') return null
  }
  return null
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
  const lines = chat?.lines ?? []
  return {
    heading: HEADING,
    sourcesTitle: SOURCES_TITLE,
    emptyThread: EMPTY_THREAD,
    noReady: NO_READY,
    emptyReason: emptyReason ?? null,
    notice: chat && !chat.askable ? chat.notice || NOTICE_DEFAULT : null,
    documentName: chat?.document_name ?? null,
    askable: chat?.askable ?? false,
    withholding: isWithholding(lines),
    openQuestion: openExaminerQuestion(lines),
    rows: chatListRows(summaries ?? []),
    lines: threadLines(lines),
    sources: sourcesFromLines(lines),
  }
}
