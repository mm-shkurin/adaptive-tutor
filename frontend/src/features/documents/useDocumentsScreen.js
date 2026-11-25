import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listDocuments, uploadDocument } from '../../shared/api/backend/documentApi'
import { addSlides, createPresentation, indexPresentation as postPresentationIndex } from '../../shared/api/backend/presentationApi'
import { presentationErrorMessage } from './logic/presentationEditorView'
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
import { FALLBACK_POLL_LIMIT, FALLBACK_POLL_MS } from './logic/statusStreamPolicy'
import { uploadErrorMessage, uploadRefusal } from './logic/uploadFile'

export function useDocumentsScreen() {
  const navigate = useNavigate()
  const [attempt, setAttempt] = useState(0)
  const [screen, setScreen] = useState({ status: 'loading' })
  const [uploading, setUploading] = useState(false)
  const [refusal, setRefusal] = useState(null)
  const [editor, setEditor] = useState(null)
  const [editorRefusal, setEditorRefusal] = useState(null)
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

  async function openPresentationEditor() {
    if (screen.status !== 'ready' || editor) return
    const controller = new AbortController()
    try {
      const presentation = await createPresentation(undefined, controller.signal)
      if (controller.signal.aborted) return
      setEditor(presentation)
      setEditorRefusal(null)
      setRefusal(null)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setRefusal(uploadErrorMessage(error))
    }
  }

  function closeEditor() {
    setEditor(null)
    setEditorRefusal(null)
    reconcileList()
  }

  async function addGallerySlides(files) {
    if (!editor || !files?.length) return
    const key = submission.current.begin(crypto.randomUUID())
    if (!key) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await addSlides(editor.id, [...files], key, controller.signal)
      if (controller.signal.aborted) return
      setEditor(updated)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    } finally {
      submission.current.finish()
    }
  }

  async function indexPresentation() {
    if (!editor) return
    const key = submission.current.begin(crypto.randomUUID())
    if (!key) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await postPresentationIndex(editor.id, key, controller.signal)
      if (controller.signal.aborted) return
      setEditor(updated)
      await reconcileList()
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    } finally {
      submission.current.finish()
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
    editor,
    editorRefusal,
    uploading,
    refusal,
    uploadPdf,
    addGallerySlides,
    indexPresentation,
    openPresentationEditor,
    closeEditor,
    retry: () => setAttempt((value) => value + 1),
  }
}

function leaveIfExpired(error, navigate) {
  if (!isSessionExpired(error)) return false
  endSession()
  navigate('/', { replace: true })
  return true
}
