import { exchangeCode, fetchProfile } from '../../../shared/api/backend/accountApi'
import { startSession } from '../../../shared/session/authSession'

const inflight = new Map()

export function exchangeOnce(code) {
  if (!inflight.has(code)) inflight.set(code, exchangeCode(code).then(startSessionFrom))
  return inflight.get(code)
}

async function startSessionFrom(tokens) {
  const session = {
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
    userId: '',
    displayName: '',
    avatarUrl: null,
  }
  startSession(session)
  try {
    const profile = await fetchProfile()
    startSession({
      ...session,
      userId: profile.id,
      displayName: profile.name,
      avatarUrl: profile.avatar_url,
      email: profile.email,
    })
  } catch {
    // Вход уже состоялся. Имя подтянется на экране профиля.
  }
}
