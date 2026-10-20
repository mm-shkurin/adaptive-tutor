import { request } from '../api/httpClient'
import { BACKEND } from '../api/backend/paths'
import { isTokenPairBody } from '../api/backend/bodyGuards'

export async function refreshTokens(refreshToken) {
  const wire = await request(BACKEND.auth.refresh, {
    method: 'POST',
    body: { refresh_token: refreshToken },
    guard: isTokenPairBody,
  })
  return { accessToken: wire.access_token, refreshToken: wire.refresh_token }
}
