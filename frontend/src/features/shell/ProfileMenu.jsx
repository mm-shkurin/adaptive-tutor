import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout } from '../../shared/api/backend/accountApi'
import { currentSession, endSession } from '../../shared/session/authSession'
import { useSession } from '../../shared/session/useSession'
import { flipTheme, subscribeToTheme, themeMenuLabel } from '../../shared/theme/themeStore'
import { avatarSrc, initialsOf, navLabel } from '../profile/logic/profileView'

export function ProfileMenu() {
  const session = useSession()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [themeLabel, setThemeLabel] = useState(themeMenuLabel)
  const name = session?.displayName ?? ''
  const shortName = navLabel(name)
  const photo = avatarSrc(session?.avatarUrl)

  useEffect(() => subscribeToTheme(() => setThemeLabel(themeMenuLabel())), [])

  useEffect(() => {
    if (!open) return undefined
    const close = (event) => {
      if (event.type === 'keydown' && event.key !== 'Escape') return
      if (event.type === 'mousedown' && event.target.closest('[data-profile-menu]')) return
      setOpen(false)
    }
    document.addEventListener('mousedown', close)
    document.addEventListener('keydown', close)
    return () => {
      document.removeEventListener('mousedown', close)
      document.removeEventListener('keydown', close)
    }
  }, [open])

  async function signOut() {
    setOpen(false)
    const current = currentSession()
    try {
      if (current) await logout(current.refreshToken)
    } catch {
      // Выход на сервере не ответил — локальную сессию всё равно закрываем.
    }
    endSession()
    navigate('/', { replace: true })
  }

  return (
    <div className="profile-menu-wrap" data-profile-menu>
      <button
        type="button"
        className="profile-trigger"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={`Меню профиля${shortName ? `: ${shortName}` : ''}`}
        data-testid="profile-menu"
        onClick={() => setOpen((value) => !value)}
      >
        {photo ? (
          <img className="nav-avatar" src={photo} alt="" data-testid="nav-avatar" />
        ) : (
          <span className="nav-avatar" data-testid="nav-avatar">
            {initialsOf(name)}
          </span>
        )}
        <span className="user-name" data-testid="nav-user-name">
          {shortName || 'Профиль'}
        </span>
        <span className="profile-chevron" aria-hidden="true" />
      </button>
      {open ? (
        <div className="profile-dropdown open" role="menu" data-testid="profile-dropdown">
          <div className="profile-dd-id">
            <div className="profile-dd-name">{name}</div>
            {session?.email ? <div className="profile-dd-email">{session.email}</div> : null}
          </div>
          <button type="button" className="profile-dd-item" role="menuitem" onClick={() => { setOpen(false); navigate('/profile') }}>
            Мой профиль
          </button>
          <button
            type="button"
            className="profile-dd-item"
            role="menuitem"
            onClick={() => {
              flipTheme()
              setThemeLabel(themeMenuLabel())
            }}
          >
            Тема: {themeLabel}
          </button>
          <button type="button" className="profile-dd-item" role="menuitem" data-testid="nav-sign-out" onClick={signOut}>
            Выйти
          </button>
        </div>
      ) : null}
    </div>
  )
}
