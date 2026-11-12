import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listDocuments, uploadDocument } from '../../shared/api/backend/documentApi'
import {
  isStreamOpenError,
  openDocumentStatusStream,
} from '../../shared/api/backend/documentStatusStream'
import { endSession } from '../../shared/session/authSession'
import { isSessionExpired } from '../../shared/session/authorizedRequest'
import {
  createListEpoch,
  createSubmission,
  fresherPage,
  needsStatusStream,
  pageWithStatusEvent,
  pageWithUploaded,
  shouldApplyUpload,
} from './logic/documentPage'
import { libraryView } from './logic/libraryView'
import { uploadErrorMessage, uploadRefusal } from './logic/uploadFile'

const FALLBACK_POLL_MS = 1000
const FALLBACK_POLL_LIMIT = 20

export function useDocumentsScreen() {
  const navigate = useNavigate()
  const [attempt, setAttempt] = useState(0)
  const [screen, setScreen] = useState({ status: 'loading' })
  const [uploading, setUploading] = useState(false)
  const [refusal, setRefusal] = useState(null)
  const lists = useRef(createListEpoch())
  const submission = useRef(createSubmission())
  const uploadAbort = useRef(null)
  const pageRef = useRef(null)

  function showPage(page, requestId) {
    if (!lists.current.accepts(requestId)) return
    const next = fresherPage(pageRef.current, page)
    pageRef.current = next
    setScreen({ status: 'ready', view: libraryView(next), page: next })
  }

  function applyStatusEvent(update) {
    const current = pageRef.current
    if (!current) return
    const next = pageWithStatusEvent(current, update)
    if (next === current) return
    lists.current.start()
    pageRef.current = next
    setScreen({ status: 'ready', view: libraryView(next), page: next })
  }

  useEffect(() => {
    const controller = new AbortController()
    const requestId = lists.current.start()
    setScreen({ status: 'loading' })
    listDocuments(controller.signal)
      .then((page) => {
        if (controller.signal.aborted) return
        showPage(page, requestId)
      })
      .catch((error) => {
        if (controller.signal.aborted) return
        if (leaveIfExpired(error, navigate)) return
        setScreen({ status: 'error' })
      })
    return () => controller.abort()
  }, [attempt, navigate])

  const inFlight =
    screen.status === 'ready' && needsStatusStream(screen.page?.documents ?? [])

  useEffect(() => {
    if (!inFlight) return undefined
    const controller = new AbortController()
    let fallbackTimer = null
    let fallbackLeft = FALLBACK_POLL_LIMIT

    function pollOnce() {
      const requestId = lists.current.start()
      listDocuments(controller.signal)
        .then((page) => {
          if (controller.signal.aborted) return
          showPage(page, requestId)
        })
        .catch((error) => {
          if (controller.signal.aborted) return
          leaveIfExpired(error, navigate)
        })
    }

    function startFallbackPoll() {
      if (fallbackTimer != null) return
      pollOnce()
      fallbackTimer = setInterval(() => {
        fallbackLeft -= 1
        if (fallbackLeft <= 0) {
          clearInterval(fallbackTimer)
          fallbackTimer = null
          return
        }
        pollOnce()
      }, FALLBACK_POLL_MS)
    }

    async function listen() {
      while (!controller.signal.aborted) {
        try {
          await openDocumentStatusStream({
            signal: controller.signal,
            onEvent: (update) => {
              if (controller.signal.aborted) return
              applyStatusEvent(update)
            },
          })
        } catch (error) {
          if (controller.signal.aborted) return
          if (leaveIfExpired(error, navigate)) return
          if (isStreamOpenError(error)) {
            startFallbackPoll()
            return
          }
          return
        }
        if (controller.signal.aborted) return
        await new Promise((resolve) => setTimeout(resolve, 500))
      }
    }

    listen()

    return () => {
      controller.abort()
      if (fallbackTimer != null) clearInterval(fallbackTimer)
    }
  }, [inFlight, navigate])

  useEffect(() => {
    const abort = uploadAbort
    const epoch = lists
    return () => {
      epoch.current.start()
      abort.current?.abort()
    }
  }, [])

  async function reconcileList() {
    const requestId = lists.current.start()
    try {
      const page = await listDocuments()
      showPage(page, requestId)
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
    }
  }

  async function uploadPdf(file) {
    if (!file || screen.status !== 'ready') return
    const refused = uploadRefusal(file)
    if (refused) {
      setRefusal(refused)
      return
    }
    const key = submission.current.begin(crypto.randomUUID())
    if (!key) return
    const controller = new AbortController()
    uploadAbort.current = controller
    setUploading(true)
    setRefusal(null)
    try {
      const uploaded = await uploadDocument(file, key, controller.signal)
      if (!shouldApplyUpload(controller.signal.aborted)) return
      const requestId = lists.current.start()
      showPage(pageWithUploaded(pageRef.current, uploaded), requestId)
    } catch (error) {
      if (!shouldApplyUpload(controller.signal.aborted)) return
      if (leaveIfExpired(error, navigate)) return
      setRefusal(uploadErrorMessage(error))
      // Server may have accepted the PDF after the client gave up (virus scan / size).
      await reconcileList()
    } finally {
      if (shouldApplyUpload(controller.signal.aborted)) {
        submission.current.finish()
        setUploading(false)
      }
    }
  }

  return {
    ...screen,
    uploading,
    refusal,
    uploadPdf,
    retry: () => setAttempt((value) => value + 1),
  }
}

function leaveIfExpired(error, navigate) {
  if (!isSessionExpired(error)) return false
  endSession()
  navigate('/', { replace: true })
  return true
}
