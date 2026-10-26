import { StrokeIcon } from '../../../shared/icons'

export function DocumentRow({ row }) {
  return (
    <div className="doc-row" data-testid="document-row">
      <div className="doc-icon">
        <StrokeIcon name="file" />
      </div>
      <div className="doc-info">
        <div className="doc-name" data-testid="document-name">
          {row.name}
        </div>
        <div className="doc-meta" data-testid="document-meta">
          {row.meta}
        </div>
        {row.failureReason ? (
          <div className="doc-failure" data-testid="document-failure">
            {row.failureReason}
          </div>
        ) : null}
      </div>
      <span className={`status-pill ${row.statusPill}`} data-testid="document-status">
        {row.statusLabel}
      </span>
    </div>
  )
}
