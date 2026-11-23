export function ChatPanelHead({
  heading,
  listOpen,
  sourcesOpen,
  onToggleList,
  onToggleSources,
  onSwitchDocument,
  onNewChat,
}) {
  return (
    <div className="panel-head">
      <h1 data-testid="chat-heading">{heading}</h1>
      <div className="panel-actions">
        <button
          type="button"
          className="btn btn-outline chat-drawer-toggle"
          data-testid="chat-list-open"
          aria-expanded={listOpen}
          onClick={onToggleList}
        >
          Чаты
        </button>
        <button
          type="button"
          className="btn btn-outline chat-drawer-toggle"
          data-testid="chat-sources-open"
          aria-expanded={sourcesOpen}
          onClick={onToggleSources}
        >
          Источники
        </button>
        <button
          type="button"
          className="btn btn-outline"
          data-testid="chat-switch-document"
          onClick={onSwitchDocument}
        >
          Сменить документ
        </button>
        <button
          type="button"
          className="btn btn-dark"
          data-testid="chat-new"
          onClick={onNewChat}
        >
          Новый чат
        </button>
      </div>
    </div>
  )
}
