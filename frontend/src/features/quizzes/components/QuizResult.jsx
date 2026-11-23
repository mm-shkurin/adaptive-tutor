import { QuizBack } from './QuizBack'

export function QuizResult({ screen }) {
  const result = screen.result
  if (!result) {
    return <p className="alert" role="alert">Не удалось открыть результат.</p>
  }
  return (
    <>
      <QuizBack onClick={screen.backToList} />
      <div className="quiz-result" data-testid="quiz-result">
        <div className="quiz-result-kicker">Результат</div>
        <div className="quiz-result-score" data-testid="quiz-score">{result.score}</div>
        <p className="quiz-result-sub" data-testid="quiz-result-sub">{result.subtitle}</p>
        <div className="quiz-review" data-testid="quiz-review">
          {result.rows.map((row) => (
            <article
              key={row.id}
              className={row.itemClass}
              data-testid="quiz-review-item"
              data-correct={row.ok ? 'true' : 'false'}
            >
              <div className="quiz-review-q" data-testid="quiz-review-question">
                {row.number}. {row.text}
              </div>
              <p className="quiz-review-a" data-testid="quiz-review-chosen">Ваш ответ: {row.chosenText}</p>
              <p className="quiz-review-a" data-testid="quiz-review-correct">Верный ответ: {row.correctText}</p>
              <p className="quiz-review-a" data-testid="quiz-review-page">{row.pageLabel}</p>
            </article>
          ))}
        </div>
        {screen.playError ? (
          <p className="alert" role="alert" data-testid="quiz-play-error">{screen.playError}</p>
        ) : null}
        <div className="quiz-nav quiz-result-nav">
          <button
            type="button"
            className="btn btn-outline"
            data-testid="quiz-back-to-list"
            onClick={screen.backToList}
          >
            К списку
          </button>
          <button
            type="button"
            className="btn btn-dark"
            data-testid="quiz-play-again"
            disabled={screen.busy}
            onClick={screen.playAgain}
          >
            Пройти ещё раз
          </button>
        </div>
      </div>
    </>
  )
}
