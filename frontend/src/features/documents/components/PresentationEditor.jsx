import { useRef } from 'react'
import { slideCardCaption, slideCountLabel } from '../logic/presentationEditorView'

const GALLERY_ACCEPT = 'image/jpeg,image/png,image/webp'

export function PresentationEditor({ screen }) {
  const presentation = screen.editor
  const galleryRef = useRef(null)
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
        />
        <button
          type="button"
          className="btn btn-dark"
          data-testid="pres-index"
          onClick={() => screen.indexPresentation()}
        >
          Готово · индексировать
        </button>
      </div>
      {screen.editorRefusal ? (
        <div className="refuse" role="alert" data-testid="pres-refusal">
          {screen.editorRefusal}
        </div>
      ) : null}
      <div className="slides-toolbar">
        <button
          type="button"
          className="btn btn-outline"
          data-testid="slide-from-gallery"
          onClick={() => galleryRef.current?.click()}
        >
          Из галереи
        </button>
        <input
          ref={galleryRef}
          type="file"
          hidden
          accept={GALLERY_ACCEPT}
          multiple
          onChange={(event) => {
            const selected = event.target.files
            event.target.value = ''
            if (selected?.length) screen.addGallerySlides(selected)
          }}
        />
        <span className="slides-count" data-testid="slides-count">
          {slideCountLabel(presentation.slide_count)}
        </span>
      </div>
      <div className="slides-grid" data-testid="slides-grid">
        {presentation.slides.map((slide) => (
          <div key={slide.id} className="slide-card" data-testid="slide-card">
            <span className="slide-num">{slide.position}</span>
            <p className="slide-card-text">{slideCardCaption(slide)}</p>
          </div>
        ))}
      </div>
    </main>
  )
}