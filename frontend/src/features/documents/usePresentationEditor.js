import { useState } from 'react'
import {
  createPresentation,
  deletePresentation as removePresentation,
  deleteSlide as removeSlide,
  getPresentation,
  patchPresentation,
} from '../../shared/api/backend/presentationApi'
import { moveSlide } from './logic/presentationOrder'
import { presentationErrorMessage } from './logic/presentationEditorView'
import { presentationDeleteConfirmed } from './logic/presentationDelete'
import { readyPdfMaterials } from './logic/presentationPdfSlides'
import { libraryView } from './logic/libraryView'
import { pageWithoutDocument } from './logic/documentPage'
import { uploadErrorMessage } from './logic/uploadFile'
import { usePresentationSlideAdds } from './usePresentationSlideAdds'

export function usePresentationEditor({
  screen,
  setScreen,
  setRefusal,
  navigate,
  leaveIfExpired,
  submission,
  pageRef,
  reconcileList,
}) {
  const [editor, setEditor] = useState(null)
  const [editorRefusal, setEditorRefusal] = useState(null)
  const slideAdds = usePresentationSlideAdds({
    editor,
    setEditor,
    setEditorRefusal,
    navigate,
    leaveIfExpired,
    submission,
    pageRef,
    reconcileList,
  })

  async function openPresentationEditor() {
    if (screen.status !== 'ready' || editor) return
    const controller = new AbortController()
    try {
      const presentation = await createPresentation(undefined, controller.signal)
      if (controller.signal.aborted) return
      setEditor(presentation)
      setEditorRefusal(null)
      setRefusal(null)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setRefusal(uploadErrorMessage(error))
    }
  }

  async function openPresentationRow(presentationId) {
    if (screen.status !== 'ready' || editor || !presentationId) return
    const controller = new AbortController()
    setRefusal(null)
    try {
      const presentation = await getPresentation(presentationId, controller.signal)
      if (controller.signal.aborted) return
      setEditor(presentation)
      setEditorRefusal(null)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setRefusal(presentationErrorMessage(error))
    }
  }

  async function renamePresentation(title) {
    if (!editor) return
    const trimmed = typeof title === 'string' ? title.trim() : ''
    if (!trimmed || trimmed === editor.title) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await patchPresentation(editor.id, { title: trimmed }, controller.signal)
      if (controller.signal.aborted) return
      setEditor(updated)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    }
  }

  async function reorderSlide(slideId, direction) {
    if (!editor) return
    const order = moveSlide(editor.slides, slideId, direction)
    if (!order) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await patchPresentation(editor.id, { slide_order: order }, controller.signal)
      if (controller.signal.aborted) return
      setEditor(updated)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    }
  }

  async function saveSlideText(slideId, text) {
    if (!editor || editor.status !== 'ready') return
    const current = editor.slides.find((slide) => slide.id === slideId)
    if (!current || current.text === text) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await patchPresentation(
        editor.id,
        { slides: [{ id: slideId, text }] },
        controller.signal,
      )
      if (controller.signal.aborted) return
      setEditor(updated)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    }
  }

  async function deleteSlide(slideId) {
    if (!editor || !slideId) return
    const controller = new AbortController()
    setEditorRefusal(null)
    try {
      const updated = await removeSlide(editor.id, slideId, controller.signal)
      if (controller.signal.aborted) return
      setEditor(updated)
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      setEditorRefusal(presentationErrorMessage(error))
    }
  }

  function closeEditor() {
    setEditor(null)
    setEditorRefusal(null)
    reconcileList()
  }

  async function deletePresentation(presentationId, { fromEditor = false } = {}) {
    const confirm =
      typeof window !== 'undefined' && typeof window.confirm === 'function'
        ? window.confirm.bind(window)
        : null
    if (!presentationDeleteConfirmed(confirm)) return
    const controller = new AbortController()
    if (fromEditor) setEditorRefusal(null)
    try {
      await removePresentation(presentationId, controller.signal)
      if (controller.signal.aborted) return
      if (fromEditor) setEditor(null)
      const next = pageWithoutDocument(pageRef.current, presentationId)
      pageRef.current = next
      if (next) {
        setScreen({ status: 'ready', view: libraryView(next), page: next })
      }
      void reconcileList()
    } catch (error) {
      if (controller.signal.aborted) return
      if (leaveIfExpired(error, navigate)) return
      const message = presentationErrorMessage(error)
      if (fromEditor) setEditorRefusal(message)
      else setRefusal(message)
    }
  }

  return {
    editor,
    editorRefusal,
    readyPdfs: readyPdfMaterials(pageRef.current?.documents ?? screen.page?.documents ?? []),
    openPresentationEditor,
    openPresentationRow,
    renamePresentation,
    reorderSlide,
    saveSlideText,
    deleteSlide,
    closeEditor,
    deletePresentation,
    ...slideAdds,
  }
}
