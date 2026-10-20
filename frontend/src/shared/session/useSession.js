import { useSyncExternalStore } from 'react'
import { currentSession, subscribeToSession } from './authSession'

export function useSession() {
  return useSyncExternalStore(subscribeToSession, currentSession, currentSession)
}
