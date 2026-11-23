export function ChatList({ rows, activeId, onSelect, open, onClose }) {
  return (
    <aside
      className={open ? 'chat-side is-open' : 'chat-side'}
      data-testid="chat-list"
    >
      <div className="chat-drawer-head">
        <span className="chat-drawer-title">Чаты</span>
        <button
          type="button"
          className="btn btn-ghost btn-sm chat-drawer-close"
          data-testid="chat-list-close"
          onClick={onClose}
        >
          Закрыть
        </button>
      </div>
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
