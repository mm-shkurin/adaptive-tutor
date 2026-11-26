import { failureText } from '../../../shared/api/failureText'
import { httpErrorIn } from '../../../shared/api/httpResponse'

export const NO_SLIDES_INDEX = 'Добавьте хотя бы один слайд.'
export const TOO_MANY_SLIDES = 'Слайдов больше 40. Уберите лишние перед индексацией.'
export const SLIDE_PLACEHOLDER = 'Текст появится после индексации'

const INDEX_REASON = {
  no_slides: NO_SLIDES_INDEX,
  too_many_slides: TOO_MANY_SLIDES,
  title_empty: 'Укажите название презентации.',
}

const ADD_REASON = {
  invalid_image: 'Нужно фото jpeg, png или webp.',
  file_too_large: 'Файл больше 50 МБ.',
  virus_detected: 'Проверка не пропустила файл.',
  slide_limit: 'В презентации уже 40 слайдов.',
  empty_add: 'Файл не выбран.',
  pdf_not_ready: 'PDF ещё не готов или недоступен.',
  pdf_page_missing: 'Такой страницы нет в выбранном PDF.',
  invalid_office: 'Нужен файл PowerPoint (.pptx) или Word (.docx).',
}

export function slideCountLabel(count) {
  const value = Math.abs(count) % 100
  const last = value % 10
  if (value > 10 && value < 20) return `${count} слайдов`
  if (last === 1) return `${count} слайд`
  if (last >= 2 && last <= 4) return `${count} слайда`
  return `${count} слайдов`
}

export function slideCardCaption(slide) {
  const trimmed = slide.text?.trim()
  if (trimmed) return trimmed
  if (slide.source === 'pdf_page' && slide.pdf_page) {
    return `Страница PDF ${slide.pdf_page}`
  }
  return SLIDE_PLACEHOLDER
}

/** Ready editor never shows slide photos — bytes are erased after index. */
export function readySlideShowsPhoto(presentationStatus) {
  return presentationStatus !== 'ready'
}

export function readySlideCardText(slide) {
  return slideCardCaption(slide)
}

export function presentationErrorMessage(error) {
  const failure = httpErrorIn(error)
  const code = failure?.errorCode
  if (code && INDEX_REASON[code]) return INDEX_REASON[code]
  if (code && ADD_REASON[code]) return ADD_REASON[code]
  return failureText(error)
}