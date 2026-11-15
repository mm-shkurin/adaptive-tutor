const MODEL_KEY = 'adaptiveTutor.chatModel'
const MODE_KEY = 'adaptiveTutor.chatMode'

export function readStoredModel(fallback = 'auto') {
  try {
    return window.localStorage.getItem(MODEL_KEY) || fallback
  } catch {
    return fallback
  }
}

export function readStoredMode(fallback = 'professor') {
  try {
    return window.localStorage.getItem(MODE_KEY) || fallback
  } catch {
    return fallback
  }
}

export function storeModel(model) {
  try {
    window.localStorage.setItem(MODEL_KEY, model)
  } catch {
    /* ignore quota */
  }
}

export function storeMode(mode) {
  try {
    window.localStorage.setItem(MODE_KEY, mode)
  } catch {
    /* ignore quota */
  }
}
