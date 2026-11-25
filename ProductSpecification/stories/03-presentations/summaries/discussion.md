## discussion (2026-11-25)

**Decision:** Interview gaps D1–D5 closed with AFK defaults (delete material only; graph nodes without edges; weak &lt;40%; sessions = distinct active days; virus on photo/office) and recorded in `AFK_ISSUES.md` / `decisions/afk-defaults-decision.md` so delivery could continue without waiting.
**Alternatives:** Stop AFK until human answers; invent edges/cascade-delete.
**Why this way:** User asked AFK to park questions in a file and keep shipping what the interview already decided.

## discussion (2026-11-25)

**Decision:** Production presentation indexing keeps `FakeOcr` until a real Tesseract adapter exists; Postgres store and HTTP path still land.
**Alternatives:** Block the store until OCR is live; call chat-LLM for every slide.
**Why this way:** Tests already require faked OCR; live poke is human (P3). Shipping persistence unblocks create/add without pretending recognition quality.
