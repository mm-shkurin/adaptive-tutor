# Quizzes — Notes & Considerations

## Warnings

### Functional Warnings

- Double-click "Generate and start" must not create two quizzes (idempotency key, same pattern as chat send).
- Model reply must be validated before commit: count ∈ {3,5,8}, four choices, exactly one correct, page ∈ retrieved piece pages. Fail → store nothing.
- Empty vector/search hit for the topic must refuse; do not invent questions.
- Card score is last **completed** attempt only; an open attempt must not overwrite it mid-run.
- Account delete today removes account + avatar only (stories 1–2 gap for docs/chats). This story must still erase quizzes and attempts for that owner.

### UI/UX Warnings

- Mockup shows "~12 min" and "с источниками" and presentations in the picker — out of scope; do not promote them to fields.
- Skip button is hidden in the mockup; do not ship it.
- Page/cite stays hidden until a choice is selected.

### Technical Warnings

- Reuse `FREE_LLM_CHAT_URL` / `HttpTutor` channel with model `auto`; do not add a second provider.
- Create is synchronous like chat send; interview set no new load ceiling vs ExpectedLoad's old 5 concurrent / P95 5s note.
- Compute-then-commit: call model only after retrieval; persist quiz only after validation. Failure after the call must leave no row.
- Branch for implementation should see `HttpTutor` (from `features/chat` until chat is on `dev`).

---

## Suggestions & Future Enhancements

### Functional Suggestions

- Story 8 reads last completed scores for weak topics / graph.
- Story 3 may later allow presentation sources; do not add slide labels now.

### Technical Suggestions

- Dedicated quiz-generation port wrapping chat completions with a quiz-shaped prompt keeps `HttpTutor` free of quiz JSON parsing if preferred.

---

## Technical Notes

### Load Considerations

- ExpectedLoad.md figures for quiz generation predate this stack. No new ceiling in interview: one sync call per create, no queue.

### Security Considerations

- IDOR: foreign quiz id → same 404 body as missing quiz.
- Error bodies must not leak document text, secrets, stacks, or paths (same as chat).
- No session → same missing-quiz refusal.

### Infrastructure Notes

- New tables for quizzes, questions, and one open attempt (plus last completed score fields on quiz). Alembic after `0011_chat_line_exam_fields`.
- Hook quiz wipe into account delete path.

### Dependencies

- Stories 1, 2, 4 required. Chat merge to `dev` is a human gate before quizzes → `dev`.

### Hazard dispositions (story-spec scan 2026-11-23)

Folded into `07_Quizzes.md` AC / Validation: hz-01 Unicode NFC round-trip + topic max 200; hz-02 inbound idempotency, atomic persist, all channel failures store nothing; hz-04 terminal choose/advance refused, account-delete wipe; hz-05 IDOR, mass-assignment ignore, omit vs null count, session-store deny, safe errors; hz-06 topic/list caps; hz-07 secret/sentinel absence; hz-08 in-flight generate lock.

Dismissed with reason:
- hz-02 outbound “partial batch retry”: create is one external call + one persist unit, not a multi-effect batch.
- hz-02 “LLM only after commit”: design is retrieve → call → validate → persist; call before persist is required to know the questions. Guard is “failed validation/persist stores nothing”, not “call after commit”.
- hz-02 distinct 4xx vs 5xx retry policy: interview/AC treat every channel failure the same (store nothing); no retry loop.
- hz-02 outer deadline vs inner timeout×retries: same sync budget as chat send; no nested retry storm.
- hz-03 multi-instance RMW latch / 409 versioning: single open attempt per quiz owned by one person; leave/resume is sequential. Concurrent cross-instance races deferred to Tier 3 if needed.
- hz-04 N−1 schema on quiz tables: greenfield tables; Story 8 reads last completed score after this story ships.
- hz-04 open-attempt expiry: interview keeps unfinished attempts indefinitely until finish or account delete.
- hz-06 pagination cursors / retry storms / pooled exhaustion: no cursor API; no auto-retry create.
- hz-07 timezone/expiry and partial fan-out visibility: not in scope.
