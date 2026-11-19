import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  createChat,
  getChat,
  listChats,
  sendChatMessage,
} from '../../shared/api/backend/chatApi'
import { endSession } from '../../shared/session/authSession'
import { isSessionExpired } from '../../shared/session/authorizedRequest'
import { readStoredMode, readStoredModel, storeMode, storeModel } from './logic/chatPrefs'
import { chatScreenView } from './logic/chatView'

export function useChatScreen() {
  const navigate = useNavigate()
  const [attempt, setAttempt] = useState(0)
  const [status, setStatus] = useState('loading')
  const [summaries, setSummaries] = useState([])
  const [chat, setChat] = useState(null)
  const [emptyReason, setEmptyReason] = useState(null)
  const [draft, setDraft] = useState('')
  const [model, setModel] = useState(() => readStoredModel())
  const [mode, setMode] = useState(() => readStoredMode())
  const [sending, setSending] = useState(false)
  const [refusal, setRefusal] = useState(null)
  const activeId = useRef(null)
  const sendLock = useRef(false)

  useEffect(() => {
    const controller = new AbortController()
    setStatus('loading')
    listChats(controller.signal)
      .then(async (listed) => {
        if (controller.signal.aborted) return
        const chats = listed.chats
        setSummaries(chats)
        if (chats.length === 0) {
          try {
            const created = await createChat(undefined, controller.signal)
            if (controller.signal.aborted) return
            activeId.current = created.id
            setChat(created)
            setSummaries([{
              id: created.id,
              document_id: created.document_id,
              document_name: created.document_name,
              preview: null,
            }])
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
      })
      .catch((error) => {
        if (controller.signal.aborted) return
        if (leaveIfExpired(error, navigate)) return
        setStatus('error')
      })
    return () => controller.abort()
  }, [attempt, navigate])

  async function selectChat(chatId) {
    if (chatId === activeId.current) return
    activeId.current = chatId
    setRefusal(null)
    try {
      const opened = await getChat(chatId)
      if (activeId.current !== chatId) return
      setChat(opened)
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setStatus('error')
    }
  }

  async function startNewChat() {
    setRefusal(null)
    try {
      const created = await createChat(chat?.document_id)
      activeId.current = created.id
      setChat(created)
      setSummaries((prev) => [
        {
          id: created.id,
          document_id: created.document_id,
          document_name: created.document_name,
          preview: null,
        },
        ...prev,
      ])
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setRefusal(error.message)
    }
  }

  function chooseModel(next) {
    setModel(next)
    storeModel(next)
  }

  function chooseMode(next) {
    const prior = mode
    setMode(next)
    storeMode(next)
    if (next === 'examiner' && prior !== 'examiner') {
      void postPayload({ mode: 'examiner' })
    }
  }

  async function sendDraft() {
    if (!chat || sendLock.current || sending) return
    const text = draft.trim()
    if (!text) {
      setRefusal('Введите сообщение.')
      return
    }
    if (!chat.askable) {
      setRefusal(chat.notice || 'Материал пока нельзя спросить.')
      return
    }
    await postPayload({ text, model, mode }, text)
  }

  async function sendTell() {
    await postPayload({ tell: true })
  }

  async function sendChoice(choiceId) {
    await postPayload({ choice_id: choiceId })
  }

  async function postPayload(payload, previewText) {
    if (!chat || sendLock.current || sending) return
    if (!chat.askable) {
      setRefusal(chat.notice || 'Материал пока нельзя спросить.')
      return
    }
    sendLock.current = true
    setSending(true)
    setRefusal(null)
    const chatId = chat.id
    const key = crypto.randomUUID()
    try {
      const result = await sendChatMessage(chatId, payload, key)
      if (activeId.current !== chatId) return
      setChat((current) => ({
        ...current,
        lines: mergeLines(current?.lines ?? [], result.lines),
      }))
      if (previewText) {
        setSummaries((prev) =>
          prev.map((row) => (row.id === chatId ? { ...row, preview: previewText } : row)),
        )
        setDraft('')
      }
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setRefusal(error.message)
    } finally {
      sendLock.current = false
      setSending(false)
    }
  }

  function openDocuments() {
    navigate('/documents')
  }

  const view = chatScreenView({ summaries, chat, emptyReason })

  return {
    status,
    view,
    chat,
    draft,
    model,
    mode,
    sending,
    refusal,
    setDraft,
    chooseModel,
    chooseMode,
    selectChat,
    startNewChat,
    sendDraft,
    sendTell,
    sendChoice,
    openDocuments,
    retry: () => setAttempt((value) => value + 1),
  }
}

function mergeLines(existing, incoming) {
  const byId = new Map(existing.map((line) => [line.id, line]))
  for (const line of incoming) {
    byId.set(line.id, line)
  }
  const order = existing.map((line) => line.id)
  for (const line of incoming) {
    if (!order.includes(line.id)) order.push(line.id)
  }
  return order.map((id) => byId.get(id))
}

function leaveIfExpired(error, navigate) {
  if (!isSessionExpired(error)) return false
  endSession()
  navigate('/', { replace: true })
  return true
}
