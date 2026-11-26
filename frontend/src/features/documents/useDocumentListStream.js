import { useEffect } from 'react'
import { listDocuments } from '../../shared/api/backend/documentApi'
import {
  isStreamOpenError,
  openDocumentStatusStream,
} from '../../shared/api/backend/documentStatusStream'
import { needsStatusStream } from './logic/documentPage'
import { FALLBACK_POLL_LIMIT, FALLBACK_POLL_MS } from './logic/statusStreamPolicy'

export function useDocumentListStream({
  screen,
  navigate,
  leaveIfExpired,
  lists,
  showPage,
  applyStatusEvent,
}) {
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
  }, [inFlight, navigate, leaveIfExpired, lists, showPage, applyStatusEvent])
}
