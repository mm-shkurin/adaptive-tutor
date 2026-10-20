import { describe, expect, it } from 'vitest'
import { avatarSrc, givenName, initialsOf, localCalendarDay, nameRefusal, navLabel, registrationLine, ROLE_LINE } from './profileView'

describe('profileView', () => {
  it('shows the local calendar day, not the UTC day', () => {
    const instant = '2026-10-13T23:30:00Z'
    expect(localCalendarDay(instant)).toBe('2026-10-14')
    expect(registrationLine(instant)).toBe('На AdaptiveTutor с 14 октября 2026')
    expect(registrationLine(instant)).not.toContain('13')
  })

  it('builds initials and keeps the student line fixed', () => {
    expect(initialsOf('Максим Шкурин')).toBe('МШ')
    expect(givenName('Максим Шкурин')).toBe('Максим')
    expect(navLabel('Александр Сергеевич')).toBe('Александр Сергее…')
    expect(navLabel('Ада')).toBe('Ада')
    expect(nameRefusal('x'.repeat(61))).toMatch(/60/)
    expect(nameRefusal('   ')).toMatch(/пробел/)
    expect(nameRefusal('')).toBeNull()
    expect(nameRefusal('x'.repeat(60))).toBeNull()
    expect(initialsOf('Ада')).toBe('А')
    expect(initialsOf('   ')).toBe('')
    expect(ROLE_LINE).toBe('Роль: Студент · ОмГТУ')
  })

  it('loads a photo through this site', () => {
    expect(avatarSrc('http://localhost:8000/api/v1/media/avatars/abc')).toBe('/api/v1/media/avatars/abc')
    expect(avatarSrc(null)).toBeNull()
  })
})
