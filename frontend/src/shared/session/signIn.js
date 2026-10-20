import { BACKEND } from '../api/backend/paths'
import { browserWindow } from '../lib/browser'

let started = false

export function resetSignIn() {
  started = false
}

export function beginSignIn() {
  if (started) return
  started = true
  browserWindow()?.location.assign(BACKEND.auth.yandexStart)
}
