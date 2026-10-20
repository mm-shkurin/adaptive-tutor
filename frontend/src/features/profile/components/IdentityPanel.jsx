import { avatarSrc, initialsOf, NAME_LIMIT, registrationLine, ROLE_LINE } from '../logic/profileView'

export function IdentityPanel({ screen }) {
  const profile = screen.profile
  const photo = avatarSrc(profile.avatar_url)
  return (
    <section className="panel">
      <h3>Личные данные</h3>
      <p className="meta">Имя и фотографию можно поменять. Пароля здесь нет — вход через Яндекс ID.</p>
      {screen.identityError ? (
        <p className="alert" role="alert" data-testid="profile-identity-error">
          {screen.identityError}
        </p>
      ) : null}
      <div className="row identity-row">
        {photo ? (
          <img className="avatar" src={photo} alt="" data-testid="profile-photo" />
        ) : (
          <div className="avatar" data-testid="profile-initials">
            {initialsOf(profile.name)}
          </div>
        )}
        <div>
          <b data-testid="profile-name">{profile.name}</b>
          <div className="meta" data-testid="profile-email">
            {profile.email}
          </div>
          <div className="meta" data-testid="profile-registered">
            {registrationLine(profile.created_at)}
          </div>
          <div className="meta" data-testid="profile-role">
            {ROLE_LINE}
          </div>
        </div>
      </div>
      <PhotoActions screen={screen} />
      {screen.editing ? <NameEditor screen={screen} /> : <NameButton screen={screen} />}
    </section>
  )
}

function PhotoActions({ screen }) {
  return (
    <div className="cta">
      <button type="button" className="btn btn-outline" onClick={() => screen.fileRef.current?.click()}>
        Изменить
      </button>
      {screen.profile.avatar_url ? (
        <button type="button" className="btn btn-ghost btn-ghost-ink" data-testid="profile-remove-photo" onClick={screen.dropPhoto}>
          Удалить фото
        </button>
      ) : null}
      <input
        ref={screen.fileRef}
        className="picker"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        data-testid="profile-photo-file"
        onChange={(event) => {
          const file = event.target.files?.[0]
          if (file) screen.pickPhoto(file)
          event.target.value = ''
        }}
      />
    </div>
  )
}

function NameButton({ screen }) {
  return (
    <div className="cta">
      <button type="button" className="btn btn-outline" data-testid="profile-edit-name" onClick={screen.startEdit}>
        Изменить имя
      </button>
    </div>
  )
}

function NameEditor({ screen }) {
  return (
    <div className="name-row">
      <input
        type="text"
        aria-label="Имя"
        data-testid="profile-name-input"
        value={screen.draft}
        maxLength={NAME_LIMIT}
        onChange={(event) => screen.setDraft(event.target.value.slice(0, NAME_LIMIT))}
      />
      <span className={screen.draft.length > NAME_LIMIT ? 'counter over' : 'counter'}>
        {screen.draft.length} / {NAME_LIMIT}
      </span>
      <button type="button" className="btn btn-dark" data-testid="profile-save" disabled={screen.saving} onClick={screen.saveName}>
        {screen.saving ? 'Сохраняем…' : 'Сохранить'}
      </button>
      <button type="button" className="btn btn-outline" data-testid="profile-cancel" onClick={screen.cancelEdit}>
        Отмена
      </button>
    </div>
  )
}
