import { canDeleteAccount } from '../logic/deleteGate'

export function AccountPanel({ screen }) {
  return (
    <section className="profile-card">
      <h2 className="profile-card-title">Аккаунт</h2>
      <p className="profile-card-sub">Выход из системы и управление данными</p>
      <div className="profile-row">
        <div>
          <div className="profile-row-label">Выйти из аккаунта</div>
          <div className="profile-row-value">Сессия закроется и на других устройствах</div>
        </div>
        <button type="button" className="btn btn-outline btn-sm" data-testid="profile-sign-out" disabled={screen.signingOut} onClick={screen.signOut}>
          Выйти
        </button>
      </div>
      <div className="profile-row">
        <div>
          <div className="profile-row-label">Удаление аккаунта</div>
          <div className="profile-row-value">Аккаунт, документы, викторины и прогресс будут удалены безвозвратно. Отменить это будет нельзя.</div>
        </div>
        <button type="button" className="btn btn-danger btn-sm" data-testid="profile-delete" onClick={screen.openDelete}>
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
        <p>Действие необратимо: будут удалены документы, история чатов, викторины и прогресс. Восстановить данные после подтверждения невозможно.</p>
        <label htmlFor="delete-email">Введите адрес аккаунта — {email} — чтобы подтвердить удаление.</label>
        <input
          id="delete-email"
          type="email"
          autoComplete="off"
          placeholder={email}
          aria-label="Почта для подтверждения"
          data-testid="delete-email"
          value={screen.deleteDraft}
          onChange={(event) => screen.setDeleteDraft(event.target.value)}
        />
        <div className="modal-actions">
          <button type="button" className="btn btn-outline btn-sm" data-testid="delete-cancel" onClick={screen.closeDelete}>
            Отмена
          </button>
          <button
            type="button"
            className="btn btn-danger btn-sm"
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
