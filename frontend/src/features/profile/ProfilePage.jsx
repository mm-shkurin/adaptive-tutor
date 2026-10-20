import { useRef } from 'react'
import { AccountPanel } from './components/AccountPanel'
import { IdentityPanel } from './components/IdentityPanel'
import { ThemePanel } from './components/ThemePanel'
import { useProfileScreen } from './useProfileScreen'

export function ProfilePage() {
  const screen = useProfileScreen()
  const fileRef = useRef(null)
  if (screen.status === 'loading') {
    return (
      <main className="main" data-testid="profile-loading">
        <div className="spinner" aria-hidden="true" />
      </main>
    )
  }
  if (screen.status === 'error') {
    return (
      <main className="main">
        <p className="alert" role="alert" data-testid="profile-error">
          Не удалось открыть профиль.
        </p>
        <button type="button" className="btn btn-primary" data-testid="profile-retry" onClick={screen.retry}>
          Повторить
        </button>
      </main>
    )
  }
  return (
    <main className="main" data-testid="profile">
      <h2>Мой профиль</h2>
      <p className="lead">Личные данные, внешний вид и аккаунт</p>
      <div className="stack">
        <IdentityPanel screen={{ ...screen, fileRef }} />
        <ThemePanel />
        <AccountPanel screen={screen} />
      </div>
    </main>
  )
}
