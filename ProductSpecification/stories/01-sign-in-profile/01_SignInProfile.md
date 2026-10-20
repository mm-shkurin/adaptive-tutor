# Sign in, landing, and profile

## Brief Description

A guest reads the landing and signs in with Yandex ID. The signed-in person edits their name and photo, switches the theme on this device, signs out, and deletes the account.

## Flow

1. Guest opens the landing and chooses sign in with Yandex.
2. Yandex confirms the person. The app opens on a session. A repeated or expired return from Yandex does not open a second account.
3. The profile shows the name, the Yandex email, «Роль: Студент · ОмГТУ», the registration date, and the photo or initials.
4. The person saves a name, or clears it and the Yandex name returns. They set or remove a photo.
5. The person picks system, light, or dark. The choice stays on this device and is painted before the first screen.
6. Sign out ends the session on every device that holds it.
7. Delete stays disabled until the typed email equals the account email. Delete removes this account only. The same Yandex identity signing in again is a new account.

## Acceptance Criteria

- Landing copy is the AdaptiveTutor mockup. The only door is Yandex ID.
- Profile, rename, photo, sign-out, and delete act only on the signed-in person. Someone else's account is untouched, and a missing person and a forbidden person look the same.
- A name of 60 characters is kept. A longer name is refused. An empty name restores the Yandex name. A rename that omits the name leaves the current name.
- A rename cannot change the email, the role line, or the registration date.
- A photo must be jpeg, png, or webp and at most 10 MB. Anything else is refused and the previous photo stays.
- Two saves or two deletes in a row produce one result, the last save that the server accepted.
- Yandex timing out, refusing, or returning an unreadable answer leaves the guest signed out.
- Errors never show the session token or the Yandex email.

## Validation Rules

| Field | Rule |
|-------|------|
| Name | 0–60 characters. Empty restores the Yandex name. |
| Photo | jpeg, png, or webp. At most 10 MB. |
| Delete confirmation | Typed email equals the account email, or delete is not sent. |
| Theme | system, light, or dark. Stored on the device. |

## Screen States

- Landing, signed out.
- Return from Yandex: waiting, signed in, or a visible failure with no session.
- Profile: saved, editing the name, saving, photo present, photo absent.
- Delete dialog: confirmation mismatch (button off), match (button on), deleted.

## Core Requirements

- «Студент · ОмГТУ» is fixed text. The university is not chosen.
- Registration date is the account's creation date, shown as the local calendar day.
- There is no email-and-password door and no guest door.
- Sign-out revokes the session on the server, not only in this browser.
