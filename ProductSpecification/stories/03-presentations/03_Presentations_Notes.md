# Presentations — Notes & Considerations

## Warnings

### Functional Warnings

- Editing ready text without re-index leaves chat on old vectors until replacement finishes — call that out in UI copy later; do not flip status off ready mid-edit (interview decision).
- Empty OCR slides stay in the deck but not in search; a deck of only empty slides must not become ready.
- Cascade-delete of chats/quizzes was not chosen; stale quiz cards need a tombstone title when the join fails.
- Graph edges are deliberately absent; do not invent co-occurrence edges from mockup lines.

### UI/UX Warnings

- Camera is a file input with `capture="environment"`, not a MediaStream API.
- Mockup weak list includes medium % — product rule is counter/list = &lt;40% only (AFK D3); do not copy mockup numbers blindly.
- «Создать презентацию» must not start a PDF upload (existing frontend guard).

### Technical Warnings

- Photo/PPTX/DOCX share the virus adapter with PDF; rate limit for ordinary PDF uploads is not extended unless a separate presentation rate appears later (interview: no new rate).
- Indexing ceiling 5 minutes / same worker pattern as PDF; 40-slide cap bounds OCR+LLM fan-out.
- Tests must fake OCR and chat-LLM (and virus/embeddings as today).

---

## Suggestions & Future Enhancements

- Graph edges once a rule exists.
- Stronger “session” definitions (duration-based).
- Live OCR poke checklist for human QA.

---

## Technical Notes

### Load Considerations

- Single-user local profile; 40 slides × OCR is the hot path. LLM only on weak OCR.
- Same ExpectedLoad posture as PDF indexing for this person's materials.

### Security Considerations

- Owner-only reads/writes; foreign id → absent shape (same as documents/quizzes).
- Virus on every new byte batch; erase bytes after successful index.
- Error bodies never include file bytes, paths, or stacks.

### Infrastructure Notes

- Local: python-pptx, python-docx, Tesseract (prod) / fake (tests), existing PyMuPDF for PDF pages, TEI, Qdrant, FREE_LLM_CHAT_URL.
- No new cloud vendor.

### Hazard fold (story altitude)

Guards expected downstream in test-spec (named here so they are not lost):

- hz-02: index / slide-add idempotency keys where double-click would duplicate; virus/OCR failure leaves no searchable half-index for that deck when the run fails wholly; empty-slide skip is per-slide not whole-deck fail.
- hz-03: concurrent edit+index / delete vs index — one winner; list does not show another owner's deck.
- hz-04: status machine draft→waiting→indexing→ready|failed; ready edit does not leave ready; delete is destructive for material only.
- hz-05: multipart type/size caps; title length; slide cap 40.
- hz-06: 5-minute index deadline; ≤40 slides.
- hz-07: failed index surfaces which slide was empty / why without internal paths.
- hz-08: out of altitude for this backend-first story draft; frontend strip owns client guards later.
