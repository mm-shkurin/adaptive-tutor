import { StrokeIcon } from '../../../shared/icons'

export function DocumentRow({ row, onOpenPresentation, onDeletePresentation }) {
  const openable = row.kind === 'presentation'
  return (
    <div className="doc-row" data-testid="document-row">
      <div className="doc-icon">
        <StrokeIcon name="file" />
      </div>
      <div className="doc-info">
        {openable ? (
          <button
            type="button"
            className="doc-name doc-name-button"
            data-testid="document-name"
            onClick={() => onOpenPresentation?.(row.id)}
          >
            {row.name}
          </button>
        ) : (
          <div className="doc-name" data-testid="document-name">
            {row.name}
          </div>
        )}
        {row.failureReason ? (
          <div className="doc-meta" data-testid="document-failure">
            {row.failureReason}
          </div>
        ) : (
          <div className="doc-meta" data-testid="document-meta">
            {row.meta}
          </div>
        )}
      </div>
      <span className={`status-pill ${row.statusPill}`} data-testid="document-status">
        {row.statusLabel}
      </span>
      {row.canDelete ? (
        <button
          type="button"
          className="btn btn-outline btn-sm doc-delete"
          data-testid="presentation-delete"
          onClick={() => onDeletePresentation?.(row.id)}
        >
          Удалить
        </button>
      ) : null}
    </div>
  )
}
