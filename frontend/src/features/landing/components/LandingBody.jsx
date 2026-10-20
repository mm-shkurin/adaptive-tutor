import { StrokeIcon } from '../../../shared/icons'
import { AUDIENCE, FAQ, FEATURES, MODES, STATS, STEPS } from '../landingCopy'

export function LandingBody({ onSignIn }) {
  return (
    <>
      <section className="section" id="features">
        <SectionHead eyebrow="Возможности" title="Что хотите сделать?" lead="Чат, викторины, документы и прогресс — в одном контуре обучения" />
        <CardGrid cards={FEATURES} kind="feature-card" testId="feature-card" />
      </section>
      <div className="stats-section">
        <div className="stats">
          {STATS.map(([value, label]) => (
            <div className="stat-card" key={label}>
              <div className="stat-val">{value}</div>
              <div className="stat-label">{label}</div>
            </div>
          ))}
        </div>
      </div>
      <section className="section-alt" id="modes">
        <div className="section section-tight">
          <SectionHead
            eyebrow="Режимы"
            title={
              <>
                <span className="accent">Выберите стиль обучения</span>
                <br />
                под задачу и уровень
              </>
            }
            lead="Один материал — четыре способа разговора с тьютором"
          />
          <CardGrid cards={MODES} kind="mode-card" />
        </div>
      </section>
      <section className="section" id="process">
        <SectionHead
          eyebrow="Процесс"
          title={
            <>
              <span className="accent">От PDF до понимания</span>
              <br />
              четыре шага без лишней суеты
            </>
          }
          lead="Загрузили материал → спросили → проверились → закрыли пробел"
        />
        <CardGrid cards={STEPS} kind="step-card" />
      </section>
      <section className="section-alt" id="audience">
        <div className="section section-tight">
          <SectionHead eyebrow="Аудитория" title="Для кого AdaptiveTutor" lead="Один продукт — разные сценарии обучения" />
          <CardGrid cards={AUDIENCE} kind="role-card" />
        </div>
      </section>
      <section className="section" id="faq">
        <SectionHead eyebrow="FAQ" title="Частые вопросы" lead="Собрали ответы на то, что обычно спрашивают первыми" />
        <div className="faq-list">
          {FAQ.map(([question, answer]) => (
            <details className="faq-item" key={question}>
              <summary>{question}</summary>
              <p className="faq-answer">{answer}</p>
            </details>
          ))}
        </div>
      </section>
      <section className="cta-band">
        <h2>Готовы учиться по своим лекциям?</h2>
        <p>Войдите и откройте чат, викторины, документы и прогресс — всё в одном месте.</p>
        <button type="button" className="btn btn-primary" onClick={onSignIn}>
          Войти и начать
        </button>
      </section>
      <footer className="landing-footer">
        <div className="footer-grid">
          <div>
            <div className="footer-brand">AdaptiveTutor</div>
            <p className="footer-about">Агентная RAG-система для обучения: объяснения с цитатами, тесты и трекинг знаний.</p>
          </div>
          <FooterCol title="Продукт" links={[['#features', 'Возможности'], ['#modes', 'Режимы'], ['#process', 'Как работает']]} />
          <FooterCol title="Инструменты" links={[['#', 'AI-тьютор'], ['#', 'Викторины'], ['#', 'Документы']]} onSignIn={onSignIn} />
          <div className="footer-col">
            <h4>Ресурсы</h4>
            <a href="#faq">FAQ</a>
            <a href="https://github.com/mm-shkurin/adaptive-tutor" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
          </div>
        </div>
        <div className="footer-bottom">© 2026 AdaptiveTutor</div>
      </footer>
    </>
  )
}

function SectionHead({ eyebrow, title, lead }) {
  return (
    <div className="section-head">
      <div className="eyebrow">{eyebrow}</div>
      <h2>{title}</h2>
      <p className="section-lead">{lead}</p>
    </div>
  )
}

function CardGrid({ cards, kind, testId }) {
  return (
    <div className="grid-4">
      {cards.map((card) => (
        <article className={kind} key={card.title} data-testid={testId}>
          {card.icon ? (
            <div className="card-icon">
              <StrokeIcon name={card.icon} />
            </div>
          ) : null}
          {card.step ? <div className="step-num">{card.step}</div> : null}
          <h3>{card.title}</h3>
          <p>{card.text}</p>
        </article>
      ))}
    </div>
  )
}

function FooterCol({ title, links, onSignIn }) {
  return (
    <div className="footer-col">
      <h4>{title}</h4>
      {links.map(([href, label]) =>
        onSignIn ? (
          <a
            key={label}
            href={href}
            onClick={(event) => {
              event.preventDefault()
              onSignIn()
            }}
          >
            {label}
          </a>
        ) : (
          <a key={label} href={href}>
            {label}
          </a>
        ),
      )}
    </div>
  )
}
