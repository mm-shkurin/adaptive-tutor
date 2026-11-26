import { readySlideCardText, slideCardCaption } from '../logic/presentationEditorView'

export function PresentationSlidesGrid({ presentation, screen }) {
  return (
    <div className="slides-grid" data-testid="slides-grid">
      {presentation.slides.map((slide) => (
        <div key={slide.id} className="slide-card" data-testid="slide-card">
          <span className="slide-num">{slide.position}</span>
          <div className="slide-card-actions">
            <button
              type="button"
              className="btn btn-outline btn-sm"
              data-testid={`slide-up-${slide.id}`}
              onClick={() => screen.reorderSlide(slide.id, 'up')}
            >
              ↑
            </button>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              data-testid={`slide-down-${slide.id}`}
              onClick={() => screen.reorderSlide(slide.id, 'down')}
            >
              ↓
            </button>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              data-testid={`slide-remove-${slide.id}`}
              onClick={() => screen.deleteSlide(slide.id)}
            >
              ×
            </button>
          </div>
          {presentation.status === 'ready' ? (
            <textarea
              className="slide-card-text slide-card-edit"
              data-testid="slide-card-text"
              defaultValue={readySlideCardText(slide)}
              aria-label={`Текст слайда ${slide.position}`}
              onBlur={(event) => screen.saveSlideText(slide.id, event.target.value)}
            />
          ) : (
            <p className="slide-card-text" data-testid="slide-card-text">
              {slideCardCaption(slide)}
            </p>
          )}
        </div>
      ))}
    </div>
  )
}
