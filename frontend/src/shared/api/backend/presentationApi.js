import { send } from '../send'
import { isPresentationBody } from './bodyGuards'
import { BACKEND } from './paths'

export function createPresentation(title, signal) {
  const body = title === undefined ? {} : { title }
  return send(BACKEND.presentations.create, {
    method: 'POST',
    body,
    signal,
    guard: isPresentationBody,
  })
}