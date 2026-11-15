## discussion (2026-11-15)

**Mistake:** Consolidation merged the empty-library screen with "a not-ready document cannot be chosen", and merged a document switch with the late reply.
**Why wrong:** Each merge narrowed the Given, so a library that still has a ready PDF, and a switch with no reply in flight, stopped being checked.
**Correct location/approach:** Those pairs stay separate: UI 0.2 and 0.3, API 7.1 and 7.2.

## discussion (2026-11-15)

**Decision:** Live embeddings use a compose TEI sidecar (`sentence-transformers/all-MiniLM-L6-v2`, OpenAI `/v1/embeddings`), not freellmapi; freellmapi stays for future chat/tutor only.
**Why:** Freellmapi rejected the MiniLM model id and failed without provider keys; acceptance already uses a 384 hash-fake and must not become the live path.
**Where applied:** `infra/docker-compose.yml` service `embeddings`, `infra/.env` `FREE_LLM_API_URL=http://embeddings:80/v1`

## discussion (2026-11-15)

**Surprise:** A real book PDF (119 pieces) failed with `search store refused` even after TEI was healthy; small fixtures indexed fine.
**Why:** Default httpx timeout was 10s while TEI needed ~8–11s for that batch on CPU; no TEI Success log during the failed attempt.
**Impact:** `HttpEmbeddings` and `HttpQdrant` timeouts are 60s; TEI needs `--auto-truncate` or long pieces return 422.
