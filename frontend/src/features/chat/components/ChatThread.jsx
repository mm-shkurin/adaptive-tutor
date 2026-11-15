export function ChatThread({ lines, emptyLabel }) {
  if (lines.length === 0) {
    return (
      <div className="messages" data-testid="chat-thread">
        <p className="chat-empty" data-testid="chat-thread-empty">
          {emptyLabel}
        </p>
      </div>
    )
  }
  return (
    <div className="messages" data-testid="chat-thread">
      {lines.map((line) => (
        <div
          key={line.id}
          className={`msg ${line.cssRole}`}
          data-testid={line.role === 'person' ? 'chat-person-line' : 'chat-tutor-line'}
        >
          <div className="msg-role">{line.roleLabel}</div>
          <div className="msg-bubble" data-testid="chat-line-text">
            {line.text}
          </div>
          {line.role === 'tutor' ? (
            <div className="msg-meta">
              {line.citation ? (
                <span className="citation" data-testid="chat-line-page">
                  {line.citation}
                </span>
              ) : null}
              {line.model ? (
                <span className="msg-model" data-testid="chat-line-model">
                  {line.model}
                </span>
              ) : null}
            </div>
          ) : null}
        </div>
      ))}
    </div>
  )
}
