import { StrokeIcon } from '../../shared/icons'
import { DocumentRow } from './components/DocumentRow'
import { useDocumentsScreen } from './useDocumentsScreen'

export function DocumentsPage() {
  const screen = useDocumentsScreen()
  if (screen.status === 'loading') {
    return (
      <main className="documents-page" data-testid="documents-loading">
        <div className="spinner" aria-hidden="true" />
      </main>
    )
  }
  if (screen.status === 'error') {
    return (
      <main className="documents-page">
        <p className="alert" role="alert" data-testid="documents-error">
          Не удалось открыть документы.
        </p>
      </main>
    )
  }
  const { view } = screen
  return (
    <main className="documents-page">
      <h1 data-testid="documents-heading">{view.heading}</h1>
      <p className="documents-lead">
        PDF или презентация из фото слайдов — оба пути попадают в индекс для чата
      </p>
      <div className="docs-entry">
        <div>
          <div className="upload-zone">
            <StrokeIcon name="upload" />
            <div data-testid="pdf-door-title">
              <strong>{view.pdfDoor.title}</strong>
            </div>
            <div className="upload-hint" data-testid="pdf-door-hint">
              {view.pdfDoor.hint}
            </div>
          </div>
        </div>
        <div className="upload-zone">
          <StrokeIcon name="screen" />
          <div data-testid="presentation-door">
            <strong>{view.presentationDoor}</strong>
          </div>
          <div className="upload-hint">фото слайдов с галереи или камеры</div>
        </div>
      </div>
      <div className="docs-section-label">Ваши материалы</div>
      <div className="docs-list" data-testid="document-list">
        {view.emptyList ? <p className="documents-empty">{view.emptyList}</p> : null}
        {view.rows.map((row) => (
          <DocumentRow key={row.id} row={row} />
        ))}
      </div>
    </main>
  )
}
