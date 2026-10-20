import { BrandMark } from '../../../shared/icons'

export function LandingNav({ onSignIn }) {
  return (
    <header className="landing-nav">
      <a className="brand" href="#top">
        <BrandMark />
        AdaptiveTutor
      </a>
      <nav className="landing-nav-links" aria-label="Разделы">
        <a href="#features">Возможности</a>
        <a href="#modes">Режимы</a>
        <a href="#process">Как работает</a>
        <a href="#audience">Для кого</a>
      </nav>
      <div className="landing-nav-actions">
        <button type="button" className="btn btn-ghost" data-testid="sign-in-yandex" onClick={onSignIn}>
          Войти
        </button>
        <button type="button" className="btn btn-primary" onClick={onSignIn}>
          Начать обучение
        </button>
      </div>
    </header>
  )
}
