import { isSessionExpired } from '../session/authorizedRequest'
import { authorizedRequest } from '../session/authorizedRequest'
import { failureText } from './failureText'

export async function send(path, options = {}) {
  try {
    return await authorizedRequest(path, options)
  } catch (error) {
    if (isSessionExpired(error)) throw error
    throw new Error(failureText(error), { cause: error })
  }
}
