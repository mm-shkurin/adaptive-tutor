import { avatarSrc, initialsOf, NAME_LIMIT, registrationLine, ROLE_LINE } from '../logic/profileView'

export function IdentityPanel({ screen }) {
  const profile = screen.profile
  const photo = avatarSrc(profile.avatar_url)
  return (
    <section className="profile-card">
      <h2 className="profile-card-title">Личные данные</h2>
      <p className="profile-card-sub">Имя и фотографию можно поменять. Пароля здесь нет — вход через Яндекс ID.</p>
      {screen.identityError ? (
        <p className="alert" role="alert" data-testid="profile-identity-error">
          {screen.identityError}
        </p>
      ) : null}
      <div className="profile-identity">
        <div className="profile-avatar-col">
          {photo ? (
            <img className="avatar lg" src={photo} alt="" data-testid="profile-photo" />
          ) : (
            <div className="avatar lg" data-testid="profile-initials">
              {initialsOf(profile.name)}
            </div>
          )}
          <PhotoActions screen={screen} />
        </div>
        <div className="profile-id-meta">
          <div className="profile-id-name" data-testid="profile-name">
            {profile.name}
          </div>
          <div className="profile-id-email" data-testid="profile-email">
            {profile.email}
          </div>
          <div className="profile-id-since" data-testid="profile-registered">
            {registrationLine(profile.created_at)}
          </div>
          <div className="profile-id-note" data-testid="profile-role">
            {ROLE_LINE}
          </div>
        </div>
      </div>
      <NameForm screen={screen} />
    </section>
  )
}

function PhotoActions({ screen }) {
  return (
    <div className="profile-avatar-actions">
      <button type="button" className="btn btn-outline btn-sm" onClick={() => screen.fileRef.current?.click()}>
        Изменить
      </button>
      {screen.profile.avatar_url ? (
        <button type="button" className="btn btn-ghost btn-sm" data-testid="profile-remove-photo" onClick={screen.dropPhoto}>
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

function NameForm({ screen }) {
  return (
    <div className="name-form">
      <label className="name-label" htmlFor="name-input">
        Имя
      </label>
      <div className="name-input-row">
        <input
          id="name-input"
          className="name-input"
          type="text"
          aria-label="Имя"
          data-testid="profile-name-input"
          value={screen.draft}
          maxLength={NAME_LIMIT}
          placeholder="Например, Анна Ковалёва"
          onChange={(event) => screen.setDraft(event.target.value.slice(0, NAME_LIMIT))}
        />
        <span className={screen.draft.length > NAME_LIMIT ? 'name-counter over' : 'name-counter'}>
          {screen.draft.length} / {NAME_LIMIT}
        </span>
      </div>
      <div className="name-actions">
        <button type="button" className="btn btn-dark btn-sm" data-testid="profile-save" disabled={screen.saving} onClick={screen.saveName}>
          {screen.saving ? 'Сохраняем…' : 'Сохранить'}
        </button>
        <button type="button" className="btn btn-outline btn-sm" data-testid="profile-cancel" onClick={screen.cancelEdit}>
          Отмена
        </button>
      </div>
    </div>
  )
}
