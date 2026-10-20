import { NavLink, Outlet } from 'react-router-dom'
import { ProfileMenu } from './ProfileMenu'

const TABS = [
  ['/chat', 'Чат'],
  ['/quizzes', 'Викторины'],
  ['/progress', 'Прогресс'],
  ['/documents', 'Документы'],
  ['/profile', 'Профиль'],
]

export function AppShell() {
  return (
    <>
      <header className="appbar">
        <NavLink className="brand brand-ink" to="/profile">
          AdaptiveTutor
        </NavLink>
        <nav className="tabs" aria-label="Разделы">
          {TABS.map(([to, label]) => (
            <NavLink key={to} to={to} className={({ isActive }) => (isActive ? 'tab on' : 'tab')}>
              {label}
            </NavLink>
          ))}
        </nav>
        <ProfileMenu />
      </header>
      <Outlet />
      <nav className="bottom" aria-label="Разделы">
        {TABS.map(([to, label]) => (
          <NavLink key={to} to={to} className={({ isActive }) => (isActive ? 'on' : undefined)}>
            {label}
          </NavLink>
        ))}
      </nav>
    </>
  )
}
