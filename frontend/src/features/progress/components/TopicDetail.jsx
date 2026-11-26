export function TopicDetail({ topic, onQuiz, onChat }) {
  if (!topic) {
    return (
      <div className="topic-detail topic-detail-empty" data-testid="topic-detail">
        <div className="topic-detail-title">Тема</div>
        <div className="topic-detail-meta">Выберите узел, чтобы открыть действия</div>
      </div>
    )
  }
  return (
    <div className="topic-detail" data-testid="topic-detail">
      <div className="topic-detail-title" data-testid="topic-detail-title">
        {topic.name}
      </div>
      <div className="topic-detail-meta" data-testid="topic-detail-meta">
        {topic.masteryLabel}
      </div>
      <div className="topic-detail-actions">
        <button
          type="button"
          className="btn btn-dark btn-sm"
          data-testid="topic-quiz"
          onClick={() => onQuiz?.(topic)}
        >
          Викторина по теме
        </button>
        <button
          type="button"
          className="btn btn-outline btn-sm"
          data-testid="topic-chat"
          onClick={() => onChat?.(topic)}
        >
          Спросить в чате
        </button>
      </div>
    </div>
  )
}
