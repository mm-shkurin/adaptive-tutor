# Interview — Story 1: Вход, лендинг и профиль

Проведено 2026-10-19. Слова пользователя: «лендинг с нашего мокапа, авторизация яндекс, профиль» и «как в мокапе: роль Студент и фиксированный вуз ОмГТУ».

## Scope

**In scope:**
- Landing copied from `adaptive-tutor-mockup.html` (texts about the tutor, not the car landing from absolute555). The sign-in button starts Yandex ID.
- Yandex ID sign-in. No email+password, no guest session.
- Profile screen: display name, photo, email from Yandex (read-only), line «Роль: Студент · ОмГТУ», date «На AdaptiveTutor с …».
- Rename (max 60 characters, same limit as absolute555 `ProfilePatch.name`).
- Change photo and remove photo.
- Theme on this device: system, light, dark.
- Sign out, which revokes the tokens on the server.
- Delete account. The person types their account email to confirm. The delete is permanent.

**Out of scope:**
- Email and password registration. The mockup says there is no password here.
- Guest login (`POST /api/v1/auth/guest/login` in absolute555). The mockup has no guest.
- Supplier application, roles, rating, reviews, deals, storefront. Those screens exist in absolute555 and stay there.
- VK ID.
- Choosing a university. ОмГТУ is a fixed line, not a field.
- Wiping chats, quizzes, and progress on delete. Those records do not exist yet. Later stories add their rows to this same delete.

**Dependencies:** None. This is the first story. Story 2 (PDF) belongs to the signed-in person.

## External API/Service Documentation

1. **Yandex ID OAuth** — https://yandex.ru/dev/id/doc/
   - The browser goes to our start URL. The provider answers our server callback. The frontend only exchanges a one-time code for a session, so the access token never sits in the address bar.

## API Endpoints Used

NOT YET IMPLEMENTED in this repo. The shapes already answer in absolute555 and are the ones we port:

- `GET /api/v1/auth/oauth/yandex/start` — redirect to Yandex
- server callback — finishes the provider handshake, hands the browser a one-time code
- `POST /api/v1/auth/oauth/exchange` — code in, access + refresh tokens out
- `POST /api/v1/auth/refresh` — new access token
- `POST /api/v1/auth/logout` — body carries the refresh token; both tokens are revoked
- `GET /api/v1/user/profile` — name, photo, email, created_at
- `PATCH /api/v1/user/profile` — `{ "name": "..." }`, empty name restores the provider name
- `PUT /api/v1/user/avatar` — multipart file
- `DELETE /api/v1/user/avatar` — back to initials
- `DELETE /api/v1/user` — delete the account. absolute555 does this with no confirmation body; our screen still requires the typed email before the call goes out

## Token/Auth Requirements

DECISION: session is the absolute555 pair, access token plus refresh token. Logout revokes both on the server. A client that only forgets its own key does not sign the person out of another device.

The profile email is the Yandex email. It is shown and used as the delete confirmation. It is not edited here.

## Key Architectural Decisions

DECISION: port the working account from absolute555 (`yandex` start, exchange, refresh, logout, profile, avatar, delete). Do not rewrite it and do not take Textery's email+password door.

DECISION: landing copy and layout come from `adaptive-tutor-mockup.html`. absolute555's landing is about cars and is not copied.

DECISION: under the name the screen shows «Роль: Студент · ОмГТУ» and the registration date from `created_at`. ОмГТУ is fixed text. The role word is «Студент», not absolute555's importer/seller role.

DECISION: theme uses absolute555's `themeStore` behavior — `system` | `light` | `dark`, stored on the device, applied before first paint. The storage key becomes this product's key, not `absolute.theme`.

DECISION: delete confirmation is the mockup's typed email. The button stays disabled until the typed value equals the account email. absolute555's API itself stays a plain `DELETE /api/v1/user`.

DECISION: name limit is 60 characters. Empty name returns the Yandex name. Both are already true in absolute555.

## Business Rules & Constraints

- Sign-in provider is Yandex ID only.
- Photo types on the mockup: jpeg, png, webp.
- Name: 1–60 characters when saving a custom name. Empty restores the provider name.
- Theme choice does not round-trip to the server.
- Delete is irreversible. The confirmation sentence names documents, chat history, quizzes, and progress, even though only the account row exists in this story.
- After delete, the same person signing in with Yandex again is a new account.

## Already Implemented (REUSE)

**In absolute555, not in this repo:**
- OAuth start, callback, exchange, refresh, logout
- Profile read, rename, avatar upload, avatar remove, delete account
- Theme switch on the device (`system` / `light` / `dark`)
- Name field max length 60

**In this repo:** nothing. The acceptance suite does not exist yet.

## NOT Yet Implemented (Gaps)

- Copy the account slice into this backend and point it at this product's users.
- Landing built from the AdaptiveTutor mockup, with the Yandex button on it.
- Profile screen with the fixed «Студент · ОмГТУ» line and the registration date.
- Delete dialog that checks the typed email before calling `DELETE /api/v1/user`.
- Theme storage key for AdaptiveTutor.

## Cross-Story Dependencies

Story 2 and everything after it run as the signed-in person. Documents, chats, quizzes, and progress are deleted when this account is deleted, each story adding its own rows to the delete that this story introduces.

## Legal/Compliance

The Yandex email and the display name are personal data. Delete removes the account row. Original lecture files are a later story; this story does not store them.

## Testing Considerations

- Fake OAuth provider in tests, the same idea as absolute555's `oauth_provider=fake`. No live Yandex call in the suite.
- Sample profile: name, email, `created_at`, with and without a photo.
- Delete button disabled until the typed email matches, enabled when it matches, rejected when it does not.

## Performance/Rate Limits

Sign-in is a redirect, not a hot path. No extra rate limit in this story beyond what the ported absolute555 account slice already enforces.
