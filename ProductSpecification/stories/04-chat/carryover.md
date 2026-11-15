## Quirk: seeded search wins over Qdrant in acceptance

**Quirk:** Acceptance search prefers a seeded in-memory store over Qdrant vectors when the document was seeded through the chat probe.
**Where:** `adapters/search/prefer_seeded_search.py`, wired only in `acceptance/support/acceptance_server.py`
**Implication:** Integration scenarios that need vectors from indexing must not call seed-search for that document; API scenarios that seed keep working unchanged.
**From:** scenario 1.1 (1.1-a-newly-indexed-pdf-is-answered-from-its-vectors-and-the-stored-starting-page)
