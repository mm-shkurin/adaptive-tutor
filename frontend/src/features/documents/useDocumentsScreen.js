import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listDocuments, uploadDocument } from '../../shared/api/backend/documentApi'
import { endSession } from '../../shared/session/authSession'
import { isSessionExpired } from '../../shared/session/authorizedRequest'
import {
  createListEpoch,
  createSubmission,
  fresherPage,
  pageWithStatusEvent,
  pageWithUploaded,
  shouldApplyUpload,
} from './logic/documentPage'
import { libraryView } from './logic/libraryView'
import { uploadErrorMessage, uploadRefusal } from './logic/uploadFile'
import { useDocumentListStream } from './useDocumentListStream'
import { usePresentationEditor } from './usePresentationEditor'

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

  useDocumentListStream({
    screen,
    navigate,
    leaveIfExpired,
    lists,
    showPage,
    applyStatusEvent,
  })

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

  const presentation = usePresentationEditor({
    screen,
    setScreen,
    setRefusal,
    navigate,
    leaveIfExpired,
    submission,
    pageRef,
    reconcileList,
  })

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
    ...presentation,
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
