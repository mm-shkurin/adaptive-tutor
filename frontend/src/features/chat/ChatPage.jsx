import { ChatScreen } from './components/ChatScreen'
import { useChatScreen } from './useChatScreen'

export function ChatPage() {
  const screen = useChatScreen()
  if (screen.status === 'loading') {
    return (
      <main className="chat-page" data-testid="chat-loading">
        <div className="spinner" aria-hidden="true" />
      </main>
    )
  }
  if (screen.status === 'error') {
    return (
      <main className="chat-page">
        <p className="alert" role="alert" data-testid="chat-error">
          Не удалось открыть чат.
        </p>
        <button type="button" className="btn btn-primary" data-testid="chat-retry" onClick={screen.retry}>
          Повторить
        </button>
      </main>
    )
  }
  return <ChatScreen screen={screen} />
}
