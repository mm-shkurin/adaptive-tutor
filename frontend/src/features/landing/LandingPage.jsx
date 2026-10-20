import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { beginSignIn, resetSignIn } from '../../shared/session/signIn'
import { useSession } from '../../shared/session/useSession'
import { WaitingGate } from '../auth/AuthGates'
import { AUDIENCE, FEATURES, MODES, STEPS } from './landingCopy'

export function LandingPage() {
  const session = useSession()
  const [starting, setStarting] = useState(false)

  useEffect(() => {
    resetSignIn()
  }, [])

  useEffect(() => {
    if (starting) beginSignIn()
  }, [starting])

  if (session) return <Navigate to="/profile" replace />
  if (starting) return <WaitingGate />

  return (
    <div data-testid="landing">
      <header className="top">
        <div className="nav">
          <a className="brand" href="#top">
            AdaptiveTutor
          </a>
          <nav className="links" aria-label="Разделы">
            <a href="#features">Возможности</a>
            <a href="#modes">Режимы</a>
            <a href="#process">Как работает</a>
            <a href="#audience">Для кого</a>
          </nav>
          <button type="button" className="btn btn-primary" data-testid="sign-in-yandex" onClick={() => setStarting(true)}>
            Войти через Яндекс
          </button>
        </div>
        <section className="hero">
          <div>
            <h1>AdaptiveTutor</h1>
            <p className="line">Учитесь по своим лекциям — с цитатами, а не догадками.</p>
            <p className="sub">AI-тьютор читает PDF, отвечает с опорой на материал и подтягивает слабые темы.</p>
            <div className="cta">
              <button type="button" className="btn btn-primary" onClick={() => setStarting(true)}>
                Войти через Яндекс
              </button>
              <a className="btn btn-ghost" href="#process">
                Как это работает
              </a>
            </div>
          </div>
          <div className="hero-visual" aria-hidden="true">
            <div className="sheet">
              <span className="meta">Лекция · PDF</span>
              <b>Линейная алгебра</b>
            </div>
            <div className="sheet">
              <span className="meta">Ответ тьютора</span>
              <b>Собственное число λ</b>
            </div>
            <div className="chip">
              Источник: <b>слайд 12, стр. 5</b>
            </div>
          </div>
        </section>
      </header>
      <CardSection id="features" eyebrow="Возможности" title="Что хотите сделать?" lead="Чат, викторины, документы и прогресс — в одном контуре обучения" cards={FEATURES} />
      <CardSection id="modes" eyebrow="Режимы" title="Четыре способа разговора" lead="Один материал — четыре режима тьютора" cards={MODES} alt />
      <CardSection id="process" eyebrow="Как работает" title="От PDF до понимания" lead="Загрузили материал, спросили, проверились, закрыли пробел" cards={STEPS} numbered />
      <CardSection id="audience" eyebrow="Для кого" title="Для кого AdaptiveTutor" lead="Один продукт — разные сценарии обучения" cards={AUDIENCE} alt />
    </div>
  )
}

function CardSection({ id, eyebrow, title, lead, cards, alt, numbered }) {
  return (
    <section className={alt ? 'section section-alt' : 'section'} id={id}>
      <div className="eyebrow">{eyebrow}</div>
      <h2>{title}</h2>
      <p className="lead">{lead}</p>
      <div className="grid">
        {cards.map((card) => (
          <article className="card" key={card[numbered ? 1 : 0]} data-testid={id === 'features' ? 'feature-card' : undefined}>
            {numbered ? <div className="step-num">{card[0]}</div> : null}
            <h3>{numbered ? card[1] : card[0]}</h3>
            <p>{numbered ? card[2] : card[1]}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
