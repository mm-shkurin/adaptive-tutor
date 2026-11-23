import { QuizBack } from './QuizBack'

export function QuizTake({ screen }) {
  const take = screen.take
  if (!take) {
    return <p className="alert" role="alert">Не удалось открыть вопрос.</p>
  }
  return (
    <>
      <QuizBack onClick={screen.backToList} />
      <div className="quiz-step-meta">
        <span data-testid="quiz-topic-title">{take.topic}</span>
        <span data-testid="quiz-position">{take.position}</span>
      </div>
      <div className="quiz-progress-bar">
        <div
          className="quiz-progress-fill"
          data-testid="quiz-progress"
          role="progressbar"
          aria-valuenow={take.progress}
          aria-valuemin={0}
          aria-valuemax={100}
          style={{ width: `${take.progress}%` }}
        />
      </div>
      <div className="quiz-question-card">
        <div className="quiz-q-num" data-testid="quiz-number">{take.number}</div>
        <div className="quiz-q-text" data-testid="quiz-question">{take.text}</div>
        <div className="quiz-options">
          {take.choices.map((choice) => (
            <button
              key={choice.id}
              type="button"
              className={choice.className}
              data-testid="quiz-choice"
              data-choice-id={choice.id}
              data-mark={choice.mark ?? ''}
              aria-disabled={take.answered || undefined}
              onClick={() => screen.choose(choice.id)}
            >
              <span className="quiz-option-key">{choice.key}</span>
              <span>{choice.text}</span>
            </button>
          ))}
        </div>
        {take.answered ? (
          <div className="quiz-cite" data-testid="quiz-reveal">
            {take.grade ? <p data-testid="quiz-grade">{take.grade}</p> : null}
            {take.page ? (
              <p data-testid="quiz-page">
                Источник: <strong>{take.page}</strong>
              </p>
            ) : null}
          </div>
        ) : null}
        {screen.playError ? (
          <p className="alert" role="alert" data-testid="quiz-play-error">{screen.playError}</p>
        ) : null}
        <div className="quiz-nav">
          <button
            type="button"
            className="btn btn-dark"
            data-testid="quiz-next"
            disabled={!take.canAdvance || screen.busy}
            onClick={screen.advance}
          >
            {take.advance}
          </button>
        </div>
      </div>
    </>
  )
}
