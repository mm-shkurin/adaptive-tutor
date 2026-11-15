export function ChatList({ rows, activeId, onSelect }) {
  return (
    <aside className="chat-side" data-testid="chat-list">
      {rows.map((row) => (
        <button
          key={row.id}
          type="button"
          className={row.id === activeId ? 'hist-item active' : 'hist-item'}
          data-testid="chat-list-row"
          data-chat-id={row.id}
          onClick={() => onSelect(row.id)}
        >
          <div className="hist-title" data-testid="chat-list-document">
            {row.documentName}
          </div>
          <div className="hist-preview" data-testid="chat-list-preview">
            {row.preview ?? ''}
          </div>
        </button>
      ))}
    </aside>
  )
}
