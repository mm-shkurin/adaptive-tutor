import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listDocuments } from '../../shared/api/backend/documentApi'
import { endSession } from '../../shared/session/authSession'
import { isSessionExpired } from '../../shared/session/authorizedRequest'
import { libraryView } from './logic/libraryView'

export function useDocumentsScreen() {
  const navigate = useNavigate()
  const [screen, setScreen] = useState({ status: 'loading' })

  useEffect(() => {
    const controller = new AbortController()
    setScreen({ status: 'loading' })
    listDocuments(controller.signal)
      .then((page) => {
        if (controller.signal.aborted) return
        setScreen({ status: 'ready', view: libraryView(page), page })
      })
      .catch((error) => {
        if (controller.signal.aborted) return
        if (isSessionExpired(error)) {
          endSession()
          navigate('/', { replace: true })
          return
        }
        setScreen({ status: 'error' })
      })
    return () => controller.abort()
  }, [navigate])

  return screen
}
