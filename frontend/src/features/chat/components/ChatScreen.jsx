import { useState } from 'react'
import { ChatDocumentPicker } from './ChatDocumentPicker'
import { ChatList } from './ChatList'
import { ChatPanelHead } from './ChatPanelHead'
import { ChatThread } from './ChatThread'
import { Composer } from './Composer'
import { SourcesPanel } from './SourcesPanel'

export function ChatScreen({ screen }) {
  const { view, chat } = screen
  const [listOpen, setListOpen] = useState(false)
  const [sourcesOpen, setSourcesOpen] = useState(false)

  function closeDrawers() {
    setListOpen(false)
    setSourcesOpen(false)
  }

  function toggleList() {
    setSourcesOpen(false)
    setListOpen((open) => !open)
  }

  function toggleSources() {
    setListOpen(false)
    setSourcesOpen((open) => !open)
  }

  function selectChat(id) {
    screen.selectChat(id)
    setListOpen(false)
  }

  return (
    <main className="chat-page" data-testid="chat-page">
      <ChatPanelHead
        heading={view.heading}
        listOpen={listOpen}
        sourcesOpen={sourcesOpen}
        onToggleList={toggleList}
        onToggleSources={toggleSources}
        onSwitchDocument={screen.beginSwitchDocument}
        onNewChat={screen.startNewChat}
      />
      {screen.documentChoices ? (
        <ChatDocumentPicker
          choices={screen.documentChoices}
          onChoose={screen.chooseDocument}
          onCancel={screen.cancelSwitchDocument}
        />
      ) : null}
      {view.emptyReason === 'no_ready' ? (
        <p className="chat-empty-state" data-testid="chat-empty-state">
          {view.noReady}
        </p>
      ) : (
        <div className="chat-layout">
          <ChatList
            rows={view.rows}
            activeId={chat?.id}
            open={listOpen}
            onClose={closeDrawers}
            onSelect={selectChat}
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
          <SourcesPanel
            title={view.sourcesTitle}
            sources={view.sources}
            open={sourcesOpen}
            onClose={closeDrawers}
          />
          {listOpen || sourcesOpen ? (
            <button
              type="button"
              className="chat-drawer-backdrop"
              data-testid="chat-drawer-backdrop"
              aria-label="Закрыть панель"
              onClick={closeDrawers}
            />
          ) : null}
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
