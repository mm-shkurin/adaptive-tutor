import {
  addSlides,
  addSlidesOfficeFile,
  addSlidesPdfPages,
  indexPresentation as postPresentationIndex,
} from '../../shared/api/backend/presentationApi'
import { presentationErrorMessage } from './logic/presentationEditorView'
import { leaveEditorAfterIndex } from './logic/presentationIndexLeave'
import { readyPdfMaterials } from './logic/presentationPdfSlides'

export function usePresentationSlideAdds({
  editor,
  setEditor,
  setEditorRefusal,
  navigate,
  leaveIfExpired,
  submission,
  pageRef,
  reconcileList,
}) {
  async function addPdfPages(pdfDocumentId, pages) {
    if (!editor || !pdfDocumentId || !pages?.length) return
    const key = submission.current.begin(crypto.randomUUID())
    if (!key) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await addSlidesPdfPages(
        editor.id,
        pdfDocumentId,
        pages,
        key,
        controller.signal,
      )
      if (controller.signal.aborted) return
      setEditor(updated)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    } finally {
      submission.current.finish()
    }
  }

  function addPdfQuickPage() {
    const materials = readyPdfMaterials(pageRef.current?.documents ?? [])
    const first = materials[0]
    if (!first) {
      setEditorRefusal('Нет готовых PDF — загрузите и дождитесь индексации.')
      return
    }
    addPdfPages(first.id, [1])
  }

  async function addOfficeFile(file) {
    if (!editor || !file) return
    const key = submission.current.begin(crypto.randomUUID())
    if (!key) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await addSlidesOfficeFile(editor.id, file, key, controller.signal)
      if (controller.signal.aborted) return
      setEditor(updated)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    } finally {
      submission.current.finish()
    }
  }

  async function addGallerySlides(files) {
    if (!editor || !files?.length) return
    const key = submission.current.begin(crypto.randomUUID())
    if (!key) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await addSlides(editor.id, [...files], key, controller.signal)
      if (controller.signal.aborted) return
      setEditor(updated)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    } finally {
      submission.current.finish()
    }
  }

  async function indexPresentation() {
    if (!editor) return
    const key = submission.current.begin(crypto.randomUUID())
    if (!key) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await postPresentationIndex(editor.id, key, controller.signal)
      if (controller.signal.aborted) return
      await reconcileList()
      if (leaveEditorAfterIndex(updated.status)) {
        setEditor(null)
        setEditorRefusal(null)
        return
      }
      setEditor(updated)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    } finally {
      submission.current.finish()
    }
  }

  return { addPdfPages, addPdfQuickPage, addOfficeFile, addGallerySlides, indexPresentation }
}
