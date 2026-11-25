import { slideCountLabel } from '../logic/presentationEditorView'

export function PresentationEditor({ screen }) {
  const presentation = screen.editor
  return (
    <main className="documents-page" data-testid="docs-editor">
      <button type="button" className="pres-back" data-testid="pres-back" onClick={screen.closeEditor}>
        ← К документам
      </button>
      <input
        className="pres-title-input"
        data-testid="pres-title"
        type="text"
        maxLength={80}
        defaultValue={presentation.title}
        aria-label="Название презентации"
      />
      <div className="slides-toolbar">
        <span className="slides-count" data-testid="slides-count">
          {slideCountLabel(presentation.slide_count)}
        </span>
      </div>
    </main>
  )
}