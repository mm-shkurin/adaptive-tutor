import { describe, expect, it } from 'vitest'
import {
  NO_SLIDES_INDEX,
  presentationErrorMessage,
  slideCardCaption,
  slideCountLabel,
} from './presentationEditorView'

function coded(errorCode, message) {
  const cause = new Error(message)
  cause.status = 400
  cause.errorCode = errorCode
  return new Error('wrapped', { cause })
}

describe('presentationEditorView', () => {
  it('slideCountLabel uses Russian plural rules', () => {
    expect(slideCountLabel(0)).toBe('0 слайдов')
    expect(slideCountLabel(1)).toBe('1 слайд')
    expect(slideCountLabel(2)).toBe('2 слайда')
    expect(slideCountLabel(5)).toBe('5 слайдов')
    expect(slideCountLabel(11)).toBe('11 слайдов')
    expect(slideCountLabel(21)).toBe('21 слайд')
  })

  it('slideCardCaption shows recognized text or a draft placeholder', () => {
    expect(slideCardCaption({ text: '  Hello  ', position: 1 })).toBe('Hello')
    expect(slideCardCaption({ text: '   ', position: 2 })).toMatch(/индексации/)
    expect(slideCardCaption({ source: 'pdf_page', pdf_page: 3, text: '' })).toBe('Страница PDF 3')
  })

  it('presentationErrorMessage maps index refusal codes', () => {
    expect(presentationErrorMessage(coded('no_slides', 'Presentation has no slides'))).toBe(NO_SLIDES_INDEX)
    expect(presentationErrorMessage(coded('invalid_image', 'Image is not supported'))).toMatch(/jpeg/)
    expect(presentationErrorMessage(coded('invalid_office', 'Office file is not supported'))).toMatch(/pptx/i)
  })
})