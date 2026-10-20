# Sign in, landing, and profile — Notes

## Warnings

### Functional Warnings

- Delete confirmation is a screen gate. `DELETE /api/v1/user` stays a plain delete for the signed-in person, as in absolute555. A client that skips the dialog can still delete. The interview chose that shape.
- Chats, quizzes, and progress do not exist yet. This delete removes the account row only. Later stories attach their rows to the same delete.
- Signing in again after delete creates a new account. Nothing of the old one comes back.

### UI/UX Warnings

- absolute555's landing is about cars. Do not copy its sections. Copy `adaptive-tutor-mockup.html`.
- The role line is the words «Студент · ОмГТУ», not absolute555's seller or importer role.
- Leaving the name form without saving discards the draft. The shown name stays the saved one.

### Technical Warnings

- Port the account slice from absolute555. Do not take Textery's email-and-password door.
- Theme storage key must not stay `absolute.theme`.
- Missing Yandex client id or secret fails at startup. It must not fall back to a guest session.

## Suggestions & Future Enhancements

### Functional Suggestions

- When documents, chats, and quizzes exist, the same delete removes them and leaves no orphan rows.

### UI/UX Suggestions

- None for this story.

### Technical Suggestions

- Keep the fake OAuth provider for tests. The suite does not call live Yandex.

## Technical Notes

### Load Considerations

Sign-in is a redirect. Expected load does not put a hot path on this story.

### Security Considerations

See the hazard scan below. Tokens and the Yandex email stay out of error bodies and logs.

### Infrastructure Notes

Yandex redirect URIs are environment settings. The ported slice already names them.

### Integration Notes

Yandex ID: https://yandex.ru/dev/id/doc/ — see `interview.md`.

The browser opens `GET /api/v1/auth/oauth/yandex/start`. Yandex returns to the server callback. The frontend exchanges a one-time code at `POST /api/v1/auth/oauth/exchange`. Refresh: `POST /api/v1/auth/refresh`. Logout: `POST /api/v1/auth/logout` with the refresh token. Profile: `GET` and `PATCH /api/v1/user/profile`. Avatar: `PUT` and `DELETE /api/v1/user/avatar`. Delete: `DELETE /api/v1/user`.

Photo byte cap ported from absolute555: `MAX_PHOTO_BYTES` default 10 MiB.

## Additional Context

See `interview.md` for the decisions this spec encodes.

## Hazard scan

Groups scanned: hz-01, hz-02, hz-03, hz-04, hz-05, hz-06, hz-07, hz-08.

| Group | Verdict | Disposition |
|-------|---------|-------------|
| hz-01 | GAP on text length | Folded: name of 60 kept, longer refused. Money and numeric precision do not fire. |
| hz-02 | GAP on replay and Yandex failure | Folded: a repeated or expired Yandex return does not open a second account. Timeout, refusal, and an unreadable answer leave the guest signed out. Outbound re-attempt of a half-written account is the same guard. Deadline budgets do not fire: one redirect, no hop chain. |
| hz-03 | GAP on overlapping saves | Folded: two saves leave the name equal to the last save the server accepted. Async queues do not fire. Seam with hz-02 closed by the single-account guard. |
| hz-04 | GAP on delete | Folded: delete removes this account only; a neighbour stays; Yandex sign-in afterwards is a new account. Schema evolution does not fire: first schema. |
| hz-05 | GAP on ownership and over-posting | Folded: only the signed-in person; missing and forbidden look the same; rename cannot change email, role line, or registration date. An omitted name leaves the current name; an empty name restores the Yandex name. Unknown or failed Yandex fails closed. |
| hz-06 | GAP on photo size | Folded: photo above 10 MB is refused and the previous photo stays. Pagination and retry storms do not fire. |
| hz-07 | GAP on disclosure and the registration day | Folded: errors never show the token or the email. The registration date is the local calendar day. Startup fails if Yandex settings are missing. |
| hz-08 | GAP on double submit | Folded: two saves or two deletes produce one result. Dirty name is discarded on leave, so the shown name stays the saved one. |

Dismissed: a server-side email body on delete. The interview keeps `DELETE /api/v1/user` plain. The screen guard is the typed-email match. Client-only confirmation is recorded in Functional Warnings, not treated as authorization.
