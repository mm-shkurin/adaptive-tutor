import { ChatList } from './ChatList'
import { ChatThread } from './ChatThread'
import { Composer } from './Composer'
import { SourcesPanel } from './SourcesPanel'

export function ChatScreen({ screen }) {
  const { view, chat } = screen
  return (
    <main className="chat-page" data-testid="chat-page">
      <div className="panel-head">
        <h1 data-testid="chat-heading">{view.heading}</h1>
        <div className="panel-actions">
          <button
            type="button"
            className="btn btn-outline"
            data-testid="chat-switch-document"
            onClick={screen.openDocuments}
          >
            Сменить документ
          </button>
          <button
            type="button"
            className="btn btn-dark"
            data-testid="chat-new"
            onClick={screen.startNewChat}
          >
            Новый чат
          </button>
        </div>
      </div>
      {view.emptyReason === 'no_ready' ? (
        <p className="chat-empty-state" data-testid="chat-empty-state">
          {view.noReady}
        </p>
      ) : (
        <div className="chat-layout">
          <ChatList
            rows={view.rows}
            activeId={chat?.id}
            onSelect={screen.selectChat}
          />
          <div className="chat-main">
            {view.notice ? (
              <p className="chat-notice" data-testid="chat-notice" role="status">
                {view.notice}
              </p>
            ) : null}
            {screen.sending ? (
              <p className="chat-working" data-testid="chat-working" role="status">
                Ответ готовится…
              </p>
            ) : null}
            {screen.refusal ? (
              <p
                className="chat-refusal"
                data-testid="chat-reply-failed"
                role="alert"
              >
                {screen.refusal}
              </p>
            ) : null}
            <ChatThread
              lines={view.lines}
              emptyLabel={view.emptyThread}
              sending={screen.sending}
              onChoice={screen.sendChoice}
            />
            <Composer
              draft={screen.draft}
              model={screen.model}
              mode={screen.mode}
              sending={screen.sending}
              askable={view.askable}
              withholding={view.withholding}
              onDraft={screen.setDraft}
              onModel={screen.chooseModel}
              onMode={screen.chooseMode}
              onSend={screen.sendDraft}
              onTell={screen.sendTell}
              onAttach={screen.openDocuments}
            />
          </div>
          <SourcesPanel title={view.sourcesTitle} sources={view.sources} />
        </div>
      )}
      {view.documentName ? (
        <span className="sr-only" data-testid="chat-bound-document">
          {view.documentName}
        </span>
      ) : null}
    </main>
  )
}
