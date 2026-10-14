# Stories — AdaptiveTutor

## MVP Stories

| # | Story | Status | Notes |
|---|-------|--------|-------|
| 1 | Document ingestion | TODO | Upload PDF, parse, extract text/tables, index in vector DB |
| 2 | Chat agent core | TODO | Planner + Retriever + Explainer pipeline |
| 3 | Quiz generation | TODO | Quizmaster agent generates questions from retrieved context |
| 4 | Knowledge Tracer basic | TODO | Student profile, weak topic tracking |
| 5 | UI dashboard | TODO | Multi-tab: Chat, Quiz, Progress, Documents |
| 6 | Citation rendering | TODO | Show source pages/slides in chat |
| 7 | Learning modes | TODO | Professor/5yo/Socratic/Examiner switches |

## Story 1: Document Ingestion

**Goal:** Instructor uploads a PDF → system parses it → extracts text/tables → generates embeddings → stores in vector DB → ready for retrieval.

**Prerequisites:** None (first story)

**Scope:**
- Upload endpoint (POST /documents)
- PDF parsing (PyMuPDF)
- Text chunking (semantic chunks, 500-1000 tokens)
- Table extraction (Camelot)
- Embedding generation (OpenAI text-embedding-3-small or local)
- Vector DB insertion (Pinecone or Qdrant)
- Metadata storage (PostgreSQL): filename, upload date, chunk count, status

**Out of scope:**
- PPTX/DOCX (future story)
- Image extraction (future story)
- Formula extraction (future story)
- Incremental updates (re-upload full document)
- Version control for documents

**Acceptance criteria:**
- Valid PDF (10 MB) → indexed in < 30 seconds
- Invalid/corrupted PDF → 400 error with clear message
- Extracted text is searchable via vector DB
- Tables are preserved as structured data
- Document status visible in UI (pending/processing/ready/failed)
