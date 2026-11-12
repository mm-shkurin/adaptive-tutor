import { describe, expect, it } from 'vitest'
import {
  MAX_PDF_BYTES,
  MIN_PDF_BYTES,
  NOT_A_PDF,
  OVER_MAXIMUM,
  RATE_LIMITED,
  UNDER_MINIMUM,
  VIRUS_BLOCKED,
  presentationDoorResult,
  uploadErrorMessage,
  uploadRefusal,
} from './uploadFile'

const file = (name, type, size) => ({ name, type, size })

function coded(errorCode, message) {
  const cause = new Error(message)
  cause.status = 400
  cause.errorCode = errorCode
  return new Error('wrapped', { cause })
}

describe('uploadFile', () => {
  it('A refused upload names the reason and leaves the list', () => {
    expect(uploadRefusal(file('notes.txt', 'text/plain', 120))).toBe(NOT_A_PDF)
    expect(uploadRefusal(file('tiny.pdf', 'application/pdf', MIN_PDF_BYTES - 1))).toBe(UNDER_MINIMUM)
    expect(uploadRefusal(file('lecture.pdf', 'application/pdf', MAX_PDF_BYTES + 1))).toBe(OVER_MAXIMUM)
    expect(uploadRefusal(file('lecture.pdf', 'application/pdf', MIN_PDF_BYTES))).toBeNull()
    expect(uploadRefusal(file('lecture.pdf', 'application/pdf', MAX_PDF_BYTES))).toBeNull()
    expect(uploadErrorMessage(coded('invalid_pdf', 'File is not a PDF'))).toBe(NOT_A_PDF)
    expect(uploadErrorMessage(coded('file_too_small', 'File is too small'))).toBe(UNDER_MINIMUM)
    expect(uploadErrorMessage(coded('file_too_large', 'File is too large'))).toBe(OVER_MAXIMUM)
    expect(uploadErrorMessage(coded('virus_detected', 'Virus detected'))).toBe(VIRUS_BLOCKED)
    expect(uploadErrorMessage(coded('rate_limited', 'Rate limited'))).toBe(RATE_LIMITED)
  })

  it('The presentation door does not upload a PDF', () => {
    expect(presentationDoorResult()).toEqual({ startsPdfUpload: false })
  })
})
