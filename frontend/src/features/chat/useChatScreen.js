import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  createChat,
  getChat,
  listChats,
  openChat,
  sendChatMessage,
} from '../../shared/api/backend/chatApi'
import { listDocuments } from '../../shared/api/backend/documentApi'
import { readStoredMode, readStoredModel, storeMode, storeModel } from './logic/chatPrefs'
import { readyDocumentChoices, summaryFromChat, upsertSummary } from './logic/chatSwitch'
import { chatScreenView } from './logic/chatView'
import { leaveIfExpired, openListedChats } from './logic/openListedChats'
import { applySendLines, shouldPaintSend } from './logic/sendResult'

export function useChatScreen() {
  const navigate = useNavigate()
  const [attempt, setAttempt] = useState(0)
  const [status, setStatus] = useState('loading')
  const [summaries, setSummaries] = useState([])
  const [chat, setChat] = useState(null)
  const [emptyReason, setEmptyReason] = useState(null)
  const [draft, setDraftState] = useState('')
  const [model, setModel] = useState(() => readStoredModel())
  const [mode, setMode] = useState(() => readStoredMode())
  const [sending, setSending] = useState(false)
  const [refusal, setRefusal] = useState(null)
  const [documentChoices, setDocumentChoices] = useState(null)
  const activeId = useRef(null)
  const sendLock = useRef(false)
  const createLock = useRef(false)
  const switchLock = useRef(false)
  const inFlight = useRef(0)
  const draftRef = useRef('')

  const setDraft = (value) => {
    draftRef.current = value
    setDraftState(value)
  }

  useEffect(() => {
    const controller = new AbortController()
    setStatus('loading')
    const state = { activeId, setChat, setSummaries, setEmptyReason, setStatus, navigate }
    listChats(controller.signal)
      .then(async (listed) => {
        if (!controller.signal.aborted) await openListedChats(listed.chats, controller, state)
      })
      .catch((error) => {
        if (!controller.signal.aborted && !leaveIfExpired(error, navigate)) setStatus('error')
      })
    return () => controller.abort()
  }, [attempt, navigate])

  async function selectChat(chatId) {
    if (chatId === activeId.current) return
    activeId.current = chatId
    setRefusal(null)
    setDocumentChoices(null)
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
    if (createLock.current) return
    createLock.current = true
    setRefusal(null)
    setDocumentChoices(null)
    try {
      const created = await createChat(chat?.document_id)
      activeId.current = created.id
      setChat(created)
      setSummaries((prev) => [summaryFromChat(created), ...prev])
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setRefusal(error.message)
    } finally {
      createLock.current = false
    }
  }

  async function beginSwitchDocument() {
    if (switchLock.current) return
    setRefusal(null)
    try {
      setDocumentChoices(readyDocumentChoices(await listDocuments()))
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setRefusal(error.message)
    }
  }

  async function chooseDocument(documentId) {
    if (switchLock.current) return
    switchLock.current = true
    setDocumentChoices(null)
    setRefusal(null)
    try {
      const opened = await openChat(documentId)
      activeId.current = opened.id
      const loaded = await getChat(opened.id)
      if (activeId.current !== opened.id) return
      setChat(loaded)
      setSummaries((prev) => upsertSummary(prev, loaded))
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setRefusal(error.message)
    } finally {
      switchLock.current = false
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
    if (next === 'examiner' && prior !== 'examiner') void postPayload({ mode: 'examiner' })
  }

  async function sendDraft() {
    if (!chat || sendLock.current) return
    const text = draftRef.current.trim()
    if (!text) {
      setRefusal('Введите сообщение.')
      return
    }
    if (!chat.askable) {
      setRefusal(chat.notice || 'Материал пока нельзя спросить.')
      return
    }
    draftRef.current = ''
    setDraftState('')
    await postPayload({ text, model, mode }, text)
  }

  async function postPayload(payload, previewText) {
    if (!chat || sendLock.current) return
    if (!chat.askable) {
      setRefusal(chat.notice || 'Материал пока нельзя спросить.')
      return
    }
    sendLock.current = true
    inFlight.current += 1
    setSending(true)
    setRefusal(null)
    const chatId = chat.id
    const key = crypto.randomUUID()
    const allowConcurrent = Boolean(previewText)
    if (allowConcurrent) sendLock.current = false
    try {
      const result = await sendChatMessage(chatId, payload, key)
      if (!shouldPaintSend(activeId.current, chatId)) return
      setChat((current) => ({
        ...current,
        lines: applySendLines(current?.lines ?? [], result.lines, activeId.current, chatId),
      }))
      if (result.error) setRefusal(result.error.message)
      if (previewText) {
        setSummaries((prev) =>
          prev.map((row) => (row.id === chatId ? { ...row, preview: previewText } : row)),
        )
      }
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      if (shouldPaintSend(activeId.current, chatId)) setRefusal(error.message)
    } finally {
      if (!allowConcurrent) sendLock.current = false
      inFlight.current = Math.max(0, inFlight.current - 1)
      setSending(inFlight.current > 0)
    }
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
    documentChoices,
    setDraft,
    chooseModel,
    chooseMode,
    selectChat,
    startNewChat,
    beginSwitchDocument,
    chooseDocument,
    cancelSwitchDocument: () => setDocumentChoices(null),
    sendDraft,
    sendTell: () => postPayload({ tell: true }),
    sendChoice: (id) => postPayload({ choice_id: id }),
    openDocuments: () => navigate('/documents'),
    retry: () => setAttempt((n) => n + 1),
  }
}
