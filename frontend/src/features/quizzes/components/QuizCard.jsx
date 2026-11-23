export function QuizCard({ card, onOpen }) {
  return (
    <button
      type="button"
      className="quiz-card"
      data-testid="quiz-card"
      data-quiz-id={card.id}
      onClick={() => onOpen(card.id)}
    >
      <span className="quiz-source" data-testid="quiz-card-document">{card.documentName}</span>
      <h3 data-testid="quiz-card-topic">{card.topic}</h3>
      <div className="quiz-meta">
        <span data-testid="quiz-card-count">{card.countLabel}</span>
      </div>
      {card.scoreText ? (
        <div className={card.scoreClass} data-testid="quiz-card-score">{card.scoreText}</div>
      ) : null}
    </button>
  )
}
