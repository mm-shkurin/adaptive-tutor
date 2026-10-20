function isRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

export function isTokenPairBody(value) {
  return isRecord(value) && typeof value.access_token === 'string' && typeof value.refresh_token === 'string'
}

export function isProfileBody(value) {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    typeof value.email === 'string' &&
    typeof value.created_at === 'string' &&
    (value.avatar_url === null || typeof value.avatar_url === 'string')
  )
}
