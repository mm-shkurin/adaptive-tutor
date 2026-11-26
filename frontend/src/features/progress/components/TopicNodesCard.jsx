import { TopicDetail } from './TopicDetail'

export function TopicNodesCard({ nodes, selectedTopicId, onSelectTopic, onQuiz, onChat }) {
  const selected = nodes.find((node) => node.id === selectedTopicId) ?? null
  return (
    <div className="prog-card" data-testid="prog-topic-nodes">
      <div className="prog-card-head">
        <div>
          <h3>Темы</h3>
          <div className="prog-card-sub">Узлы без рёбер — только список усвоения</div>
        </div>
      </div>
      {nodes.length === 0 ? (
        <p className="prog-empty">Пока нет тем по выбранным материалам.</p>
      ) : (
        <ul className="prog-node-list">
          {nodes.map((node) => (
            <li key={node.id}>
              <button
                type="button"
                className={`prog-node-row${node.id === selectedTopicId ? ' is-selected' : ''}`}
                data-testid={`prog-topic-${node.id}`}
                onClick={() => onSelectTopic?.(node.id)}
              >
                <span className={`prog-band-dot ${node.bandClass}`} aria-hidden="true" />
                <span className="prog-node-name">{node.name}</span>
                <span className="prog-node-mastery" data-testid={`prog-topic-mastery-${node.id}`}>
                  {node.masteryLabel}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
      <div className="kg-legend">
        <span>
          <i className="prog-band-mastered" aria-hidden="true" />
          Усвоено ≥70%
        </span>
        <span>
          <i className="prog-band-medium" aria-hidden="true" />
          Средне 40–69%
        </span>
        <span>
          <i className="prog-band-weak" aria-hidden="true" />
          Слабо &lt;40%
        </span>
      </div>
      <TopicDetail topic={selected} onQuiz={onQuiz} onChat={onChat} />
    </div>
  )
}