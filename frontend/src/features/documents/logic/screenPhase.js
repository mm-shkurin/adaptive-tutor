export function screenPhase(status) {
  if (status === 'loading') return { status, error: null, retry: null }
  if (status === 'error') {
    return { status, error: 'Не удалось открыть документы.', retry: 'Повторить' }
  }
  return { status, error: null, retry: null }
}
