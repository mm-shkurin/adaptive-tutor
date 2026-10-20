import { canDeleteAccount } from '../logic/deleteGate'

export function AccountPanel({ screen }) {
  return (
    <section className="panel">
      <div className="split">
        <div>
          <b>Выйти из аккаунта</b>
          <div className="meta">Сессия закроется и на других устройствах</div>
        </div>
        <button type="button" className="btn btn-outline" data-testid="profile-sign-out" disabled={screen.signingOut} onClick={screen.signOut}>
          Выйти
        </button>
      </div>
      <div className="split">
        <div>
          <b>Удаление аккаунта</b>
          <div className="meta">Документы, чаты, викторины и прогресс будут удалены безвозвратно</div>
        </div>
        <button type="button" className="btn btn-danger" data-testid="profile-delete" onClick={screen.openDelete}>
          Удалить аккаунт
        </button>
      </div>
      {screen.deleteOpen ? <DeleteDialog screen={screen} /> : null}
    </section>
  )
}

function DeleteDialog({ screen }) {
  const email = screen.profile.email
  return (
    <div className="backdrop">
      <section className="modal" role="dialog" aria-labelledby="delete-title" data-testid="delete-dialog">
        <h2 id="delete-title">Удалить аккаунт?</h2>
        <p>Действие необратимо. Восстановить данные после подтверждения нельзя.</p>
        <label htmlFor="delete-email">Введите адрес аккаунта — {email} — чтобы подтвердить удаление.</label>
        <input
          id="delete-email"
          type="email"
          aria-label="Почта для подтверждения"
          data-testid="delete-email"
          value={screen.deleteDraft}
          onChange={(event) => screen.setDeleteDraft(event.target.value)}
        />
        <div className="modal-actions">
          <button type="button" className="btn btn-outline" data-testid="delete-cancel" onClick={screen.closeDelete}>
            Отмена
          </button>
          <button
            type="button"
            className="btn btn-danger"
            data-testid="delete-confirm"
            disabled={!canDeleteAccount(screen.deleteDraft, email) || screen.deleting}
            onClick={screen.confirmDelete}
          >
            Удалить аккаунт
          </button>
        </div>
      </section>
    </div>
  )
}
