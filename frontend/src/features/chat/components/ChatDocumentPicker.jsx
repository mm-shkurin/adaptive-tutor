export function ChatDocumentPicker({ choices, onChoose, onCancel }) {
  return (
    <div className="chat-document-picker" data-testid="chat-document-picker">
      {choices.map((doc) => (
        <button
          key={doc.id}
          type="button"
          className="btn btn-outline"
          data-testid="chat-document-choice"
          data-document-name={doc.name}
          onClick={() => onChoose(doc.id)}
        >
          {doc.name}
        </button>
      ))}
      <button
        type="button"
        className="btn"
        data-testid="chat-document-picker-cancel"
        onClick={onCancel}
      >
        Отмена
      </button>
    </div>
  )
}
