import { QuizCard } from './QuizCard'

export function QuizList({ screen }) {
  return (
    <>
      <div className="panel-head">
        <div>
          <h1>Викторины</h1>
          <p className="quiz-lead">Вопросы по готовому PDF, со ссылкой на страницу.</p>
        </div>
        <div className="panel-actions">
          <button
            type="button"
            className="btn btn-dark"
            data-testid="quiz-create-open"
            onClick={screen.openCreate}
          >
            Создать викторину
          </button>
        </div>
      </div>
      {screen.formNotice ? (
        <p className="quiz-lead" data-testid={screen.formNotice.id}>{screen.formNotice.text}</p>
      ) : null}
      {screen.listError ? (
        <p className="alert" role="alert" data-testid="quiz-list-error">{screen.listError}</p>
      ) : null}
      {screen.cards.length === 0 ? (
        <p className="quiz-empty" data-testid="quiz-empty">Пока нет викторин.</p>
      ) : null}
      <div className="quiz-grid" data-testid="quiz-list">
        {screen.cards.map((card) => (
          <QuizCard key={card.id} card={card} onOpen={screen.openQuiz} />
        ))}
        <button
          type="button"
          className="quiz-card quiz-create-card"
          data-testid="quiz-create-tile"
          onClick={screen.openCreate}
        >
          <span className="quiz-create-plus" aria-hidden="true">+</span>
          <strong>Новая викторина</strong>
          <span className="quiz-create-note">по готовому PDF</span>
        </button>
      </div>
    </>
  )
}
