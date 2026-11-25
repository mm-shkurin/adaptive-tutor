export function WeakTopicsCard({ topics }) {
  return (
    <div className="prog-card" data-testid="prog-weak-list">
      <div className="prog-card-head">
        <div>
          <h3>Слабые темы</h3>
          <div className="prog-card-sub">Стоит повторить перед экзаменом</div>
        </div>
      </div>
      {topics.length === 0 ? (
        <p className="prog-empty">Нет тем ниже 40%.</p>
      ) : (
        <div>
          {topics.map((topic) => (
            <div key={topic.id} className="weak-row" data-testid={`prog-weak-${topic.id}`}>
              <span className="weak-name">{topic.name}</span>
              <span className="weak-score bad" data-testid={`prog-weak-mastery-${topic.id}`}>
                {topic.masteryLabel}
              </span>
              <div className="weak-bar">
                <span style={{ width: topic.barWidth }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}