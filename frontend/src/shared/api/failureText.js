import { httpErrorIn } from './httpResponse'
import { isRequestTimeout } from './requestTimeout'

const BY_CODE = {
  invalid_name: 'Имя не длиннее 60 символов и не из одних пробелов. Прежнее имя осталось.',
  invalid_photo: 'Нужна фотография jpeg, png или webp. Прежняя осталась.',
  photo_too_large: 'Фотография больше 10 МБ. Прежняя осталась.',
}

const GENERIC = 'Не получилось. Попробуйте ещё раз.'

export function failureText(error) {
  if (isRequestTimeout(error) || isRequestTimeout(error?.cause)) {
    return 'Сервер не ответил вовремя. Проверьте связь и попробуйте ещё раз.'
  }
  if (error?.name === 'UnexpectedBodyError' || error?.cause?.name === 'UnexpectedBodyError') {
    return 'Сервер вернул ответ, который экран не смог прочитать.'
  }
  const failure = httpErrorIn(error)
  if (!failure) return GENERIC
  if (failure.errorCode && BY_CODE[failure.errorCode]) return BY_CODE[failure.errorCode]
  if (failure.status === 413) return BY_CODE.photo_too_large
  if (failure.status === 422) return BY_CODE.invalid_name
  if (failure.status >= 500) return 'Сервис временно недоступен. Попробуйте позже.'
  return GENERIC
}
