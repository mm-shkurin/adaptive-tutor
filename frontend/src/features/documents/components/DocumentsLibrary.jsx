import { StrokeIcon } from '../../../shared/icons'
import { presentationDoorResult } from '../logic/uploadFile'
import { DocumentRow } from './DocumentRow'

export function DocumentsLibrary({ screen, fileRef }) {
  const { view } = screen
  return (
    <main className="documents-page">
      <h1 data-testid="documents-heading">{view.heading}</h1>
      <p className="documents-lead">
        PDF или презентация из фото слайдов — оба пути попадают в индекс для чата
      </p>
      <div className="docs-entry">
        <div>
          <div
            className="upload-zone"
            role="button"
            tabIndex={0}
            data-testid="pdf-door"
            onClick={() => fileRef.current?.click()}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') fileRef.current?.click()
            }}
          >
            <StrokeIcon name="upload" />
            <div data-testid="pdf-door-title">
              <strong>{view.pdfDoor.title}</strong>
            </div>
            <div className="upload-hint" data-testid="pdf-door-hint">
              {view.pdfDoor.hint}
            </div>
            <input
              ref={fileRef}
              type="file"
              hidden
              data-testid="pdf-upload-input"
              disabled={screen.uploading}
              onChange={(event) => {
                const file = event.target.files?.[0]
                event.target.value = ''
                if (file) screen.uploadPdf(file)
              }}
            />
          </div>
          {screen.refusal ? (
            <div className="refuse" role="alert" data-testid="upload-refusal">
              {screen.refusal}
            </div>
          ) : null}
        </div>
        <button
          type="button"
          className="upload-zone"
          onClick={() => {
            if (presentationDoorResult().startsPdfUpload) fileRef.current?.click()
          }}
        >
          <StrokeIcon name="screen" />
          <div data-testid="presentation-door">
            <strong>{view.presentationDoor}</strong>
          </div>
          <div className="upload-hint">фото слайдов с галереи или камеры</div>
        </button>
      </div>
      <div className="docs-section-label">Ваши материалы</div>
      <div className="docs-list" data-testid="document-list">
        {view.emptyList ? (
          <p className="documents-empty" data-testid="documents-empty">
            {view.emptyList}
          </p>
        ) : null}
        {view.rows.map((row) => (
          <DocumentRow key={row.id} row={row} />
        ))}
      </div>
    </main>
  )
}
