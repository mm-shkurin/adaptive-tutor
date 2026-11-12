# Backlog (out of current story)

## From story 2 — PDF-документы

- **Real embeddings + Qdrant.** Interview decided freellmapi `/v1/embeddings` (384-d) and self-hosted Qdrant. Delivered instead: text pieces + extracted text in Postgres (`PostgresPieceIndex`); embedding refusal/server_error only as Fake/Probe `_refusal` seam — **no Embedding port, no Qdrant client, no vector write path.** Needed before RAG chat retrieval (stories 4–5). `QDRANT_URL` is already a startup gate with no live client behind it.
