import { StrokeIcon } from '../../../shared/icons'
import { MODELS, MODES } from '../logic/chatView'

export function Composer({
  draft,
  model,
  mode,
  sending,
  askable,
  onDraft,
  onModel,
  onMode,
  onSend,
  onAttach,
}) {
  return (
    <div className="composer" data-testid="chat-composer">
      <textarea
        data-testid="chat-input"
        placeholder="Сообщение для AdaptiveTutor"
        rows={2}
        value={draft}
        disabled={!askable || sending}
        onChange={(event) => onDraft(event.target.value)}
      />
      <div className="composer-bar">
        <div className="composer-left">
          {MODES.map((item) => (
            <button
              key={item.id}
              type="button"
              className={item.id === mode ? 'mode-btn active' : 'mode-btn'}
              data-testid={`chat-mode-${item.id}`}
              onClick={() => onMode(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <div className="composer-right">
          <select
            className="model-select"
            data-testid="chat-model"
            aria-label="Модель"
            value={model}
            onChange={(event) => onModel(event.target.value)}
          >
            {MODELS.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="composer-icon-btn"
            data-testid="chat-attach"
            title="Прикрепить"
            aria-label="Прикрепить"
            onClick={onAttach}
          >
            <StrokeIcon name="paperclip" />
          </button>
          <button
            type="button"
            className="composer-send"
            data-testid="chat-send"
            aria-label="Отправить"
            disabled={!askable || sending}
            onClick={onSend}
          >
            <StrokeIcon name="send" />
          </button>
        </div>
      </div>
    </div>
  )
}
