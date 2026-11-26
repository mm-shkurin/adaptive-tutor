import { NavLink, Outlet } from 'react-router-dom'
import { BrandMark, StrokeIcon } from '../../shared/icons'
import { ProfileMenu } from './ProfileMenu'

const TABS = [
  ['/chat', 'Чат', 'chat'],
  ['/quizzes', 'Викторины', 'quiz'],
  ['/progress', 'Прогресс', 'chart'],
  ['/documents', 'Документы', 'docs'],
  ['/profile', 'Профиль', 'user'],
]

function tabTestId(to) {
  if (to === '/documents') return 'documents-tab'
  if (to === '/chat') return 'chat-tab'
  if (to === '/quizzes') return 'quizzes-tab'
  if (to === '/progress') return 'progress-tab'
  return undefined
}

export function AppShell() {
  return (
    <>
      <header className="appbar">
        <NavLink className="brand brand-ink" to="/profile">
          <BrandMark />
          AdaptiveTutor
        </NavLink>
        <nav className="tabs" aria-label="Разделы">
          {TABS.map(([to, label, icon]) => (
            <NavLink
              key={to}
              to={to}
              data-testid={tabTestId(to)}
              className={({ isActive }) => (isActive ? 'tab on' : 'tab')}
            >
              <StrokeIcon name={icon} />
              <span className="label">{label}</span>
            </NavLink>
          ))}
        </nav>
        <ProfileMenu />
      </header>
      <Outlet />
      <nav className="bottom" aria-label="Разделы">
        {TABS.map(([to, label]) => (
          <NavLink
            key={to}
            to={to}
            data-testid={tabTestId(to)}
            className={({ isActive }) => (isActive ? 'on' : undefined)}
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </>
  )
}
