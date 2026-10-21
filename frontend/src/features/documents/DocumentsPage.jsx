import { StrokeIcon } from '../../shared/icons'
import { libraryView } from './logic/libraryView'

const EMPTY_PAGE = { documents: [], has_next: false }

export function DocumentsPage() {
  const view = libraryView(EMPTY_PAGE)
  return (
    <main className="documents-page">
      <h1 data-testid="documents-heading">{view.heading}</h1>
      <p className="documents-lead">
        PDF или презентация из фото слайдов — оба пути попадают в индекс для чата
      </p>
      <div className="docs-entry">
        <div className="upload-zone">
          <StrokeIcon name="upload" />
          <div data-testid="pdf-door-title">
            <strong>{view.pdfDoor.title}</strong>
          </div>
          <div className="upload-hint" data-testid="pdf-door-hint">
            {view.pdfDoor.hint}
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
      </div>
    </main>
  )
}
