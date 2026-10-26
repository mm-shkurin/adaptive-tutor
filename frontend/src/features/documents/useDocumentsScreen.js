import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listDocuments, uploadDocument } from '../../shared/api/backend/documentApi'
import { endSession } from '../../shared/session/authSession'
import { isSessionExpired } from '../../shared/session/authorizedRequest'
import { needsStatusPoll, pageWithUploaded } from './logic/documentPage'
import { libraryView } from './logic/libraryView'

const POLL_MS = 250

export function useDocumentsScreen() {
  const navigate = useNavigate()
  const [screen, setScreen] = useState({ status: 'loading' })
  const [uploading, setUploading] = useState(false)
  const uploadLock = useRef(false)
  const pageRef = useRef(null)

  useEffect(() => {
    const controller = new AbortController()
    setScreen({ status: 'loading' })
    listDocuments(controller.signal)
      .then((page) => {
        if (controller.signal.aborted) return
        showPage(page)
      })
      .catch((error) => {
        if (controller.signal.aborted) return
        if (leaveIfExpired(error, navigate)) return
        setScreen({ status: 'error' })
      })
    return () => controller.abort()
  }, [navigate])

  useEffect(() => {
    if (screen.status !== 'ready') return undefined
    if (!needsStatusPoll(screen.page.documents)) return undefined
    const controller = new AbortController()
    const timer = setInterval(() => {
      listDocuments(controller.signal)
        .then((page) => {
          if (controller.signal.aborted) return
          showPage(page)
        })
        .catch((error) => {
          if (controller.signal.aborted) return
          leaveIfExpired(error, navigate)
        })
    }, POLL_MS)
    return () => {
      controller.abort()
      clearInterval(timer)
    }
  }, [screen, navigate])

  function showPage(page) {
    pageRef.current = page
    setScreen({ status: 'ready', view: libraryView(page), page })
  }

  async function uploadPdf(file) {
    if (!file || uploadLock.current || screen.status !== 'ready') return
    uploadLock.current = true
    setUploading(true)
    try {
      const uploaded = await uploadDocument(file, crypto.randomUUID())
      const next = pageWithUploaded(pageRef.current ?? screen.page, uploaded)
      showPage(next)
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setScreen({ status: 'error' })
    } finally {
      uploadLock.current = false
      setUploading(false)
    }
  }

  return { ...screen, uploading, uploadPdf }
}

function leaveIfExpired(error, navigate) {
  if (!isSessionExpired(error)) return false
  endSession()
  navigate('/', { replace: true })
  return true
}
