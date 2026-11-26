export function ActivityCard({ items }) {
  return (
    <div className="prog-card" data-testid="prog-activity">
      <div className="prog-card-head">
        <div>
          <h3>Недавняя активность</h3>
          <div className="prog-card-sub">Что влияло на граф знаний</div>
        </div>
      </div>
      {items.length === 0 ? (
        <p className="prog-empty">Пока нет активности по материалам.</p>
      ) : (
        <div className="activity-list">
          {items.map((item) => (
            <div key={item.id} className="activity-row" data-testid={`prog-activity-${item.kind}`}>
              <span className={`activity-dot${item.warn ? ' warn' : ''}`} aria-hidden="true" />
              <div>
                <div className="activity-title">{item.title}</div>
                <div className="activity-meta">{item.meta}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
