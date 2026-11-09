import { useRef } from 'react'
import { DocumentsLibrary } from './components/DocumentsLibrary'
import { screenPhase } from './logic/screenPhase'
import { useDocumentsScreen } from './useDocumentsScreen'

export function DocumentsPage() {
  const screen = useDocumentsScreen()
  const fileRef = useRef(null)
  const phase = screenPhase(screen.status)
  if (phase.status === 'loading') {
    return (
      <main className="documents-page" data-testid="documents-loading">
        <div className="spinner" aria-hidden="true" />
      </main>
    )
  }
  if (phase.status === 'error') {
    return (
      <main className="documents-page">
        <p className="alert" role="alert" data-testid="documents-error">
          {phase.error}
        </p>
        <button type="button" className="btn btn-primary" data-testid="documents-retry" onClick={screen.retry}>
          {phase.retry}
        </button>
      </main>
    )
  }
  return <DocumentsLibrary screen={screen} fileRef={fileRef} />
}
