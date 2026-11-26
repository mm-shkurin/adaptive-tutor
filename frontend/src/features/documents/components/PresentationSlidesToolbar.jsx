import { useRef, useState } from 'react'
import { parsePdfPageList } from '../logic/presentationPdfSlides'
import { slideCountLabel } from '../logic/presentationEditorView'

const GALLERY_ACCEPT = 'image/jpeg,image/png,image/webp'
const OFFICE_ACCEPT =
  '.pptx,.docx,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/vnd.openxmlformats-officedocument.wordprocessingml.document'

export function PresentationSlidesToolbar({ screen, presentation, readyPdfs }) {
  const galleryRef = useRef(null)
  const cameraRef = useRef(null)
  const officeRef = useRef(null)
  const [pdfId, setPdfId] = useState(readyPdfs[0]?.id ?? '')
  const [pageList, setPageList] = useState('1')
  const selectedPdf = readyPdfs.find((pdf) => pdf.id === pdfId) ?? readyPdfs[0]

  function submitPdfPages(pages) {
    if (!selectedPdf || !pages.length) return
    screen.addPdfPages(selectedPdf.id, pages)
  }

  return (
    <div className="slides-toolbar">
      <button
        type="button"
        className="btn btn-outline"
        data-testid="slide-from-gallery"
        onClick={() => galleryRef.current?.click()}
      >
        Из галереи
      </button>
      <button
        type="button"
        className="btn btn-outline"
        data-testid="slide-from-camera"
        onClick={() => cameraRef.current?.click()}
      >
        Камера
      </button>
      <button
        type="button"
        className="btn btn-outline"
        data-testid="slide-from-office"
        onClick={() => officeRef.current?.click()}
      >
        PPTX / DOCX
      </button>
      <input
        ref={galleryRef}
        type="file"
        hidden
        accept={GALLERY_ACCEPT}
        multiple
        data-testid="slide-gallery-input"
        onChange={(event) => {
          const selected = event.target.files
          event.target.value = ''
          if (selected?.length) screen.addGallerySlides(selected)
        }}
      />
      <input
        ref={cameraRef}
        type="file"
        hidden
        accept={GALLERY_ACCEPT}
        capture="environment"
        onChange={(event) => {
          const selected = event.target.files
          event.target.value = ''
          if (selected?.length) screen.addGallerySlides(selected)
        }}
      />
      <input
        ref={officeRef}
        type="file"
        hidden
        accept={OFFICE_ACCEPT}
        onChange={(event) => {
          const selected = event.target.files?.[0]
          event.target.value = ''
          if (selected) screen.addOfficeFile(selected)
        }}
      />
      {readyPdfs.length > 0 ? (
        <div className="slides-pdf-add" data-testid="slide-pdf-picker">
          <select
            className="slides-pdf-select"
            data-testid="slide-pdf-select"
            value={selectedPdf?.id ?? ''}
            onChange={(event) => setPdfId(event.target.value)}
            aria-label="Готовый PDF"
          >
            {readyPdfs.map((pdf) => (
              <option key={pdf.id} value={pdf.id}>
                {pdf.name}
              </option>
            ))}
          </select>
          <input
            className="slides-pdf-pages"
            data-testid="slide-pdf-pages"
            type="text"
            inputMode="numeric"
            aria-label="Номера страниц"
            value={pageList}
            onChange={(event) => setPageList(event.target.value)}
          />
          <button
            type="button"
            className="btn btn-outline"
            data-testid="slide-from-pdf"
            onClick={() => submitPdfPages(parsePdfPageList(pageList, selectedPdf?.page_count))}
          >
            Из PDF
          </button>
          <button
            type="button"
            className="btn btn-outline"
            data-testid="slide-pdf-page-1"
            onClick={() => screen.addPdfQuickPage()}
          >
            Стр. 1
          </button>
        </div>
      ) : null}
      <span className="slides-count" data-testid="slides-count">
        {slideCountLabel(presentation.slide_count)}
      </span>
    </div>
  )
}
