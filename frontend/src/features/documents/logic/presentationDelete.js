export const DELETE_PRESENTATION_PROMPT = 'Удалить эту презентацию? Её нельзя будет восстановить.'

export function presentationDeleteConfirmed(confirmFn, accepted) {
  if (typeof confirmFn !== 'function') return accepted === true
  return confirmFn(DELETE_PRESENTATION_PROMPT) === true
}