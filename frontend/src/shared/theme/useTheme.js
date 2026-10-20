import { useSyncExternalStore } from 'react'
import { setTheme, subscribeToTheme, themeChoice } from './themeStore'

export function useTheme() {
  const choice = useSyncExternalStore(subscribeToTheme, themeChoice, themeChoice)
  return { choice, setTheme }
}
