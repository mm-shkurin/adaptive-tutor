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
