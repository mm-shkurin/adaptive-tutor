import { useEffect, useRef } from 'react'

export function ChatThread({ lines, emptyLabel, onChoice, sending }) {
  const threadRef = useRef(null)

  useEffect(() => {
    const root = threadRef.current
    if (!root) return
    root.scrollTop = root.scrollHeight
  }, [lines.length, sending])

  if (lines.length === 0) {
    return (
      <div className="messages" data-testid="chat-thread" ref={threadRef}>
        <p className="chat-empty" data-testid="chat-thread-empty">
          {emptyLabel}
        </p>
      </div>
    )
  }
  return (
    <div className="messages" data-testid="chat-thread" ref={threadRef}>
      {lines.map((line) => (
        <div
          key={line.id}
          className={`msg ${line.cssRole}`}
          data-testid={line.role === 'person' ? 'chat-person-line' : 'chat-tutor-line'}
          data-kind={line.kind ?? undefined}
        >
          <div className="msg-role">{line.roleLabel}</div>
          <div className="msg-bubble" data-testid="chat-line-text">
            {line.text}
          </div>
          {line.gradeLabel ? (
            <div className="msg-grade" data-testid="chat-grade-label">
              {line.gradeLabel}
            </div>
          ) : null}
          {line.choices.length > 0 ? (
            <div className="msg-choices" data-testid="chat-choices">
              {line.choices.map((choice) => (
                <button
                  key={choice.id}
                  type="button"
                  className="choice-btn"
                  data-testid={`chat-choice-${choice.id}`}
                  disabled={sending}
                  onClick={() => onChoice?.(choice.id)}
                >
                  {choice.text}
                </button>
              ))}
            </div>
          ) : null}
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
