import { send } from '../send'
import { request } from '../httpClient'
import { isProfileBody, isTokenPairBody } from './bodyGuards'
import { BACKEND } from './paths'
import { updateIdentity } from '../../session/authSession'

export async function fetchProfile(signal) {
  const profile = await send(BACKEND.user.profile, { signal, guard: isProfileBody })
  updateIdentity(profile.name, profile.avatar_url, profile.email)
  return profile
}

export function renameProfile(name) {
  return send(BACKEND.user.profile, { method: 'PATCH', body: { name }, guard: isProfileBody })
}

export function uploadAvatar(file) {
  const form = new FormData()
  form.append('file', file)
  return send(BACKEND.user.avatar, { method: 'PUT', body: form, guard: isProfileBody })
}

export function removeAvatar() {
  return send(BACKEND.user.avatar, { method: 'DELETE', guard: isProfileBody })
}

export function logout(refreshToken) {
  return send(BACKEND.auth.logout, { method: 'POST', body: { refresh_token: refreshToken } })
}

export function deleteAccount() {
  return send(BACKEND.user.account, { method: 'DELETE' })
}

export function exchangeCode(code) {
  return request(BACKEND.auth.oauthExchange, {
    method: 'POST',
    body: { code },
    guard: isTokenPairBody,
  })
}
