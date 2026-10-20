export const MAX_PHOTO_BYTES = 10 * 1024 * 1024

const TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])
const EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

const TYPE_MESSAGE = 'Нужна фотография jpeg, png или webp. Прежняя осталась.'
const SIZE_MESSAGE = 'Фотография больше 10 МБ. Прежняя осталась.'

export function photoRefusal(file) {
  const named = EXTENSIONS.some((extension) => file.name.toLowerCase().endsWith(extension))
  const allowed = file.type ? TYPES.has(file.type) : named
  if (!allowed) return TYPE_MESSAGE
  if (file.size > MAX_PHOTO_BYTES) return SIZE_MESSAGE
  return null
}
