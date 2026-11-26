import {
  indexButtonLabel,
  indexFailureBanner,
} from '../logic/presentationEditorView'
import { PresentationSlidesGrid } from './PresentationSlidesGrid'
import { PresentationSlidesToolbar } from './PresentationSlidesToolbar'

export function PresentationEditor({ screen }) {
  const presentation = screen.editor
  const readyPdfs = screen.readyPdfs ?? []
  const failure = indexFailureBanner(presentation)

  return (
    <main className="documents-page" data-testid="docs-editor">
      <button type="button" className="pres-back" data-testid="pres-back" onClick={screen.closeEditor}>
        ← К документам
      </button>
      <div className="pres-editor-head">
        <input
          className="pres-title-input"
          data-testid="pres-title"
          type="text"
          maxLength={80}
          defaultValue={presentation.title}
          aria-label="Название презентации"
          onBlur={(event) => screen.renamePresentation(event.target.value)}
        />
        <div className="pres-editor-actions">
          <button
            type="button"
            className="btn btn-outline btn-sm"
            data-testid="pres-delete"
            onClick={() => screen.deletePresentation(presentation.id, { fromEditor: true })}
          >
            Удалить
          </button>
          <button
            type="button"
            className="btn btn-dark"
            data-testid="pres-index"
            disabled={presentation.status === 'indexing'}
            onClick={() => screen.indexPresentation()}
          >
            {indexButtonLabel(presentation.status)}
          </button>
        </div>
      </div>
      {failure ? (
        <div className="refuse" role="alert" data-testid="pres-index-failure">
          {failure}
        </div>
      ) : null}
      {screen.editorRefusal ? (
        <div className="refuse" role="alert" data-testid="pres-refusal">
          {screen.editorRefusal}
        </div>
      ) : null}
      <PresentationSlidesToolbar screen={screen} presentation={presentation} readyPdfs={readyPdfs} />
      <PresentationSlidesGrid presentation={presentation} screen={screen} />
    </main>
  )
}
