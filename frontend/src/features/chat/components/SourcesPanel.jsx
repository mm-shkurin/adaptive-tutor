export function SourcesPanel({ title, sources }) {
  return (
    <aside className="source-side" data-testid="chat-sources">
      <div className="source-title">{title}</div>
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
