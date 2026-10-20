import { describe, expect, it } from 'vitest'
import { MAX_PHOTO_BYTES, photoRefusal } from './photoFile'

const file = (name, type, size) => ({ name, type, size })

describe('photoRefusal', () => {
  it('accepts jpeg, png and webp up to 10 MB', () => {
    expect(photoRefusal(file('a.jpg', 'image/jpeg', 100))).toBeNull()
    expect(photoRefusal(file('a.png', 'image/png', MAX_PHOTO_BYTES))).toBeNull()
    expect(photoRefusal(file('a.webp', '', 100))).toBeNull()
  })

  it('refuses anything else and does not mention an email', () => {
    expect(photoRefusal(file('a.gif', 'image/gif', 100))).toMatch(/jpeg/)
    expect(photoRefusal(file('a.jpg', 'image/jpeg', MAX_PHOTO_BYTES + 1))).toMatch(/10 МБ/)
    expect(photoRefusal(file('a.gif', 'image/gif', 100))).not.toMatch(/@/)
  })
})
