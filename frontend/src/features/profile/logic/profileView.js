export const ROLE_LINE = 'Роль: Студент · ОмГТУ'

const MONTHS = [
  'января',
  'февраля',
  'марта',
  'апреля',
  'мая',
  'июня',
  'июля',
  'августа',
  'сентября',
  'октября',
  'ноября',
  'декабря',
]

export function registrationLine(iso) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return `На AdaptiveTutor с ${date.getDate()} ${MONTHS[date.getMonth()]} ${date.getFullYear()}`
}

export function localCalendarDay(iso) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}

export const NAME_LIMIT = 60
export const NAV_NAME_LIMIT = 16

export function nameRefusal(raw) {
  if (raw === '') return null
  const trimmed = raw.trim()
  if (!trimmed) return 'Имя не может состоять из пробелов.'
  if (trimmed.length > NAME_LIMIT) return 'Имя не длиннее 60 символов.'
  return null
}

export function navLabel(name) {
  const text = name.trim()
  if (text.length <= NAV_NAME_LIMIT) return text
  return `${text.slice(0, NAV_NAME_LIMIT).trimEnd()}…`
}

export function givenName(name) {
  return name.trim().split(/\s+/).filter(Boolean)[0] ?? ''
}

export function initialsOf(name) {
  const words = name.trim().split(/\s+/).filter(Boolean)
  if (words.length === 0) return ''
  const letters = words.length === 1 ? words[0].slice(0, 1) : words[0].slice(0, 1) + words[words.length - 1].slice(0, 1)
  return letters.toLocaleUpperCase('ru')
}

export function avatarSrc(url) {
  if (!url) return null
  try {
    const parsed = new URL(url, 'http://localhost')
    if (parsed.pathname.startsWith('/api/')) return `${parsed.pathname}${parsed.search}`
  } catch {
    return url
  }
  return url
}
