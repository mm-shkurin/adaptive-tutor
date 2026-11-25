import { send } from '../send'
import { isProgressBody } from './bodyGuards'
import { BACKEND } from './paths'

export function fetchProgress(materialId, signal) {
  const path =
    materialId != null && materialId !== ''
      ? `${BACKEND.progress}?material=${encodeURIComponent(materialId)}`
      : BACKEND.progress
  return send(path, { signal, guard: isProgressBody })
}