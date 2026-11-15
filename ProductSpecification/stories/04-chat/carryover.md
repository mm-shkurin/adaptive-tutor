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
