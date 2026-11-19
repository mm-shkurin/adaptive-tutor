import { createChat, getChat } from '../../../shared/api/backend/chatApi'
import { isSessionExpired } from '../../../shared/session/authorizedRequest'
import { endSession } from '../../../shared/session/authSession'
import { summaryFromChat } from './chatSwitch'

export async function openListedChats(chats, controller, state) {
  const { activeId, setChat, setSummaries, setEmptyReason, setStatus, navigate } = state
  setSummaries(chats)
  if (chats.length === 0) {
    try {
      const created = await createChat(undefined, controller.signal)
      if (controller.signal.aborted) return
      activeId.current = created.id
      setChat(created)
      setSummaries([summaryFromChat(created)])
      setEmptyReason(null)
      setStatus('ready')
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setChat(null)
      setEmptyReason('no_ready')
      setStatus('ready')
    }
    return
  }
  const selected = chats[0]
  activeId.current = selected.id
  const opened = await getChat(selected.id, controller.signal)
  if (controller.signal.aborted) return
  setChat(opened)
  setEmptyReason(null)
  setStatus('ready')
}

export function leaveIfExpired(error, navigate) {
  if (!isSessionExpired(error)) return false
  endSession()
  navigate('/', { replace: true })
  return true
}
