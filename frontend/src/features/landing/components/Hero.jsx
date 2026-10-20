export function Hero({ onSignIn }) {
  return (
    <section className="hero" aria-label="Главный экран">
      <div className="hero-copy">
        <h1 className="hero-brand">AdaptiveTutor</h1>
        <p className="hero-line">Учитесь по своим лекциям — с цитатами, а не догадками.</p>
        <p className="hero-sub">AI-тьютор читает PDF, отвечает с опорой на материал и подтягивает слабые темы.</p>
        <div className="hero-cta">
          <button type="button" className="btn btn-primary" onClick={onSignIn}>
            Войти
          </button>
          <a className="btn btn-ghost" href="#process">
            Как это работает
          </a>
        </div>
      </div>
      <div className="hero-visual" aria-hidden="true">
        <div className="hero-plane">
          <div className="doc-stack">
            <DocSheet label="Лекция · PDF" title="Линейная алгебра" />
            <DocSheet label="Ответ тьютора" title="Собственное число λ" />
            <DocSheet label="Режим · Профессор" title="Характеристическое уравнение" />
          </div>
          <div className="cite-chip">
            Источник: <strong>слайд 12, стр. 5</strong>
          </div>
        </div>
      </div>
    </section>
  )
}

function DocSheet({ label, title }) {
  return (
    <div className="doc-sheet">
      <div className="doc-label">{label}</div>
      <div className="doc-title">{title}</div>
      <div className="doc-lines">
        <span />
        <span />
        <span />
      </div>
    </div>
  )
}
