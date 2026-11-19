## Quirk: seeded search wins over Qdrant in acceptance

**Quirk:** Acceptance search prefers a seeded in-memory store over Qdrant vectors when the document was seeded through the chat probe.
**Where:** `adapters/search/prefer_seeded_search.py`, wired only in `acceptance/support/acceptance_server.py`
**Implication:** Integration scenarios that need vectors from indexing must not call seed-search for that document; API scenarios that seed keep working unchanged.
**From:** scenario 1.1 (1.1-a-newly-indexed-pdf-is-answered-from-its-vectors-and-the-stored-starting-page)

## Quirk: ready-without-vectors clears post-index points

**Quirk:** A ready PDF with no vectors is set up by finishing indexing, then clearing that document's points from the embedding/Qdrant fake — failing the embedding during indexing would mark the document failed instead.
**Where:** `acceptance/support/vector_fakes.py` (`clear_vectors`), `acceptance/statements/vector_open_statements.py`
**Implication:** Open-time vector scenarios must clear post-index vectors; do not reuse the indexing embedding-refusal probe path.
**From:** scenario 1.2 (1.2-a-vector-run-that-fails-leaves-the-document-ready-and-the-next-open-can-finish)

## Quirk: production send still uses RefusingTutor

**Quirk:** `application/context.py` wires `RefusingTutor` into `SendMessage`, so every non-acceptance send stores a person line with `reply_failed` and no tutor line.
**Where:** `backend/application/context.py`, `adapters/tutor/refusing_tutor.py`
**Implication:** Happy-path tutor answers need a real HTTP tutor adapter; until then failed-reply is the live path.
**From:** scenario 6.6 (6.6-a-failed-reply-keeps-one-person-line)

## Quirk: interleave opens must gather on the server

**Quirk:** Two sync HTTP clients racing a vector latch deadlock the single uvicorn loop.
**Where:** `acceptance/support/chat_probe.py` (`/acceptance/chats/{id}/interleave-open`)
**Implication:** Concurrent open races use in-process `asyncio.gather`, not ThreadPool HTTP.
**From:** scenario 6.10 (6.10-two-opens-interleaved-do-not-store-a-piece-twice)

## Quirk: vector ready is full piece-set equality

**Quirk:** `QdrantPieces.ready` is true only when Qdrant count equals `PieceIndex` length — `count > 0` would mark a mid-fail run askable.
**Where:** `backend/adapters/search/qdrant_pieces.py`
**Implication:** Open-time and send paths must treat partial vector sets as not askable; writes skip ordinals already present.
**From:** scenario 6.4 (6.4-a-vector-run-that-stops-midway)

## Quirk: clear_vectors leaves upsert log

**Quirk:** `clear_vectors` removes points but leaves the fake upsert log, so absolute `upsert_count` still includes indexing.
**Where:** `acceptance/support/vector_fakes.py`, partial-vector statements
**Implication:** Assert upsert deltas around the open under test, not the absolute total.
**From:** scenario 6.4 (6.4-a-vector-run-that-stops-midway)

## Decision: acceptance chat latency is 50ms

**Decision:** Acceptance pins `SendMessage` latency at 50ms; production stays at ExpectedLoad P99 5s.
**Why:** Wall-clock 5s hangs do not change the expire/cancel contract under test.
**Where applied:** `SendMessage(latency=...)` in `AcceptanceServer`; `CHAT_LATENCY` in `reply_budget.py`
**From:** scenario 6.8 (6.8-a-reply-that-misses-the-latency-budget)

## Quirk: POST /chats/open does not vectorize

**Quirk:** `OpenChat` returns the store chat (or a newly created one) without running `GetChat.open`, so `askable` may stay false until a later GET.
**Where:** `backend/usecase/chat/open_chat.py`, `adapters/http/chats.py` `POST /open`
**Implication:** Switch/open is identity only; vectorization stays on GET, same as create.
**From:** scenario 7.1 (7.1-switching-document-keeps-the-previous-chat)

## Quirk: late reply + switch needs tutor hold probe

**Quirk:** A late reply while switching needs an in-process tutor hold plus `reply-after-switch` probe; client ThreadPool cannot beat the 50ms acceptance latency budget.
**Where:** `acceptance/support/tutor_hold.py`, `acceptance/support/chat_probe.py`, `ScriptedTutor.hold`
**Implication:** Interleave send-then-switch on the server event loop; do not hang the tutor with `sleep(30)`.
**From:** scenario 7.2 (7.2-a-reply-to-the-chat-just-left-stays-on-that-chat)

## Quirk: failed/unknown document status setup paths

**Quirk:** `move` cannot jump waiting→failed or set an unknown status; failed needs indexing first, unknown needs `probe.force_document_status`.
**Where:** `domain/document/document.py` (`transition`), `acceptance/clients/application/index_probe.py` (`force_document_status`)
**Implication:** Gate setups for failed/unknown must follow those paths, not a single move call.
**From:** scenario 1.2 (1.2-a-document-that-is-not-ready-cannot-be-bound)
