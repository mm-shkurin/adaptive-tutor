export function SourcesPanel({ title, sources, open, onClose }) {
  return (
    <aside
      className={open ? 'source-side is-open' : 'source-side'}
      data-testid="chat-sources"
    >
      <div className="chat-drawer-head">
        <span className="chat-drawer-title">{title}</span>
        <button
          type="button"
          className="btn btn-ghost btn-sm chat-drawer-close"
          data-testid="chat-sources-close"
          onClick={onClose}
        >
          Закрыть
        </button>
      </div>
      {sources.map((source) => (
        <div key={source.key} className="source-card" data-testid="chat-source-card">
          {source.pageLabel ? (
            <div className="source-page" data-testid="chat-source-page">
              {source.pageLabel}
            </div>
          ) : null}
          <div className="source-text" data-testid="chat-source-text">
            {source.text}
          </div>
        </div>
      ))}
    </aside>
  )
}
