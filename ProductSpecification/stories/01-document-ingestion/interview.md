# Interview — Story 1: Document Ingestion

## Scope

**In scope:**
- Upload PDF files (text-based only, no OCR in this story)
- Parse PDF with PyMuPDF
- Extract text and tables
- Semantic chunking (by paragraphs/headers, min 500 tokens)
- Convert tables to Markdown and include in text chunks
- Generate embeddings using freellmapi (free tier, 7.4B tokens/month, smart routing across 34 providers)
- Store embeddings in Qdrant (self-hosted via Docker)
- Store metadata in PostgreSQL (filename, upload date, chunk count, status)
- Async background processing (upload returns ID immediately, processing in background)
- Extended validation: PDF only, max 50 MB, non-empty, ClamAV virus scan, encrypted PDF check
- Rate limiting: 5 uploads per minute
- Custom error codes for processing failures

**Out of scope:**
- OCR for scanned PDFs (future story)
- PPTX/DOCX support (future story)
- Image extraction (future story)
- Formula extraction (future story)
- Incremental document updates (re-upload full document)
- Version control for documents
- Original file storage (ephemeral — delete after indexing)

**Dependencies:** None (first story)

## External API/Service Documentation

**Cloud API (freellmapi):**
1. **freellmapi** — LLM/Embedding routing service
   - Docs: https://github.com/tashfeenahmed/freellmapi
   - Free tier: 7.4B tokens/month across 34 providers
   - OpenAI-compatible `/v1/embeddings` endpoint
   - Smart routing, automatic failover, encrypted keys
   - Self-hosted or cloud (freellmapi.co)

**Self-hosted (Docker):**
2. **Qdrant** — Vector database (Docker)
   - Docs: https://qdrant.tech/documentation/
   - Local deployment via Docker Compose

3. **ClamAV** — Virus scanning (Docker)
   - Docs: https://docs.clamav.net/
   - Local deployment via Docker Compose

## API Endpoints Used

NOT YET IMPLEMENTED:

**Backend endpoints to create:**
- `POST /api/v1/documents` — Upload PDF file
  - Request: multipart/form-data with file
  - Response: document_id, status (pending/processing/ready/failed)
  - Validation: PDF only, max 50 MB, non-empty
  - Rate limit: 5 uploads/minute

- `GET /api/v1/documents/{id}` — Get document status
  - Response: document_id, filename, status, chunk_count, created_at, error_message (if failed)

- `GET /api/v1/documents` — List all documents
  - Response: list of documents with basic metadata

## Token/Auth Requirements

NOT YET IMPLEMENTED:

MVP: No authentication (public upload for instructor role)
Future: JWT-based auth for instructor/admin roles

## Key Architectural Decisions

**DECISION: Vector DB — Qdrant (self-hosted)**
- Rationale: Free, full control, no cloud dependencies for MVP
- Trade-off: Requires DevOps for Docker setup vs Pinecone's managed service

**DECISION: Embedding model — freellmapi (free tier)**
- Rationale: Free (7.4B tokens/month), higher quality than local models, smart routing across 34 providers, automatic failover
- Trade-off: Requires internet connectivity, dependency on external service uptime

**DECISION: Processing — Async background**
- Rationale: Large files (up to 50 MB) can take > 30s to process; synchronous would timeout
- Implementation: FastAPI BackgroundTasks or Celery
- Trade-off: More complex vs synchronous, but necessary for UX

**DECISION: File storage — Ephemeral**
- Rationale: Storage costs, security (no need to keep original after indexing)
- Trade-off: Cannot re-process without re-upload; no audit trail of original files

**DECISION: Chunking — Semantic chunks**
- Rationale: Preserves meaning by paragraph/header boundaries vs fixed-size breaking context
- Implementation: PyMuPDF text extraction → paragraph detection → 500 token minimum chunks
- Trade-off: Slightly more complex than fixed-size, but better retrieval quality

**DECISION: Table handling — Markdown in text**
- Rationale: Simple approach, tables participate in semantic search with surrounding context
- Trade-off: Less structured than separate table chunks, but easier implementation

**DECISION: Validation — Extended**
- Rationale: Security (virus scan), UX (encrypted PDF detection prevents silent failures)
- Implementation: ClamAV for viruses, PyMuPDF check for encryption
- Trade-off: More dependencies (ClamAV) vs basic validation

**DECISION: Error handling — Custom error codes**
- Rationale: Better UX than generic HTTP errors, easier debugging
- Examples: FILE_TOO_LARGE, INVALID_PDF, VIRUS_DETECTED, ENCRYPTED_PDF, CHUNKING_FAILED, EMBEDDING_FAILED, VECTOR_DB_FAILED

## Business Rules & Constraints

**File constraints:**
- File type: PDF only (application/pdf)
- File size: 1-50 MB (min 1 MB to avoid empty uploads, max 50 MB per ExpectedLoad)
- Content: Non-empty, not encrypted/protected
- Security: Must pass ClamAV virus scan

**Processing constraints:**
- Processing time: < 30 seconds for 10 MB PDF (ExpectedLoad SLA)
- Chunk size: Minimum 500 tokens, semantic boundaries preferred
- Embedding dimension: 384 (all-MiniLM-L6-v2)
- Rate limit: 5 uploads per minute per IP/user

**Status transitions:**
- pending → processing → ready (success)
- pending → processing → failed (error)
- Failed documents store error_message for debugging

**Cross-story constraints:**
- Document status must be queryable by Chat agent (Story 2)
- Vector DB must be searchable by Retriever agent (Story 2)
- Document metadata must be displayable in UI (Story 5)

## Already Implemented (REUSE)

**Nothing exists** — new project, starting from scratch.

## NOT Yet Implemented (Gaps)

**Backend:**
- FastAPI project structure (hexagonal architecture)
- PostgreSQL schema and migrations (Alembic)
- Qdrant Docker setup and client configuration
- ClamAV Docker setup and integration
- PyMuPDF PDF parsing logic
- Semantic chunking logic
- freellmapi setup (local or cloud deployment)
- OpenAI-compatible client for embeddings API
- Background task processing (BackgroundTasks or Celery)
- Custom error code exceptions
- Rate limiting middleware
- Document upload endpoint
- Document status endpoint
- Document list endpoint

**Infrastructure:**
- Docker Compose file (PostgreSQL, Qdrant, ClamAV)
- .env configuration template
- Database connection pooling

**Testing:**
- Unit tests for PDF parsing
- Unit tests for chunking logic
- Integration tests for upload endpoint
- Integration tests for Qdrant insertion
- Load tests for concurrent uploads

## Cross-Story Dependencies

**Story 2 (Chat agent core) depends on:**
- Vector DB populated with document chunks
- Document metadata accessible via API
- Searchable chunks with embeddings

**Story 5 (UI dashboard) depends on:**
- Document list endpoint
- Document status endpoint
- Document status transitions (pending/processing/ready/failed)

**No dependencies on:** Story 3 (Quiz generation), Story 4 (Knowledge Tracer), Story 6 (Citation rendering), Story 7 (Learning modes)

## Legal/Compliance

**Data privacy:**
- Ephemeral file storage (no original files retained after indexing)
- No PII in document metadata (filename only, no user tracking in MVP)

**Security:**
- Virus scanning required (ClamAV)
- File type validation (PDF only)
- File size limits (prevent DoS)
- Rate limiting (prevent abuse)

**Future compliance (not MVP):**
- GDPR user consent for document storage
- Data retention policies
- Audit logging for document access

## Testing Considerations

**Test modes:**
- Local Qdrant instance for integration tests
- Mock ClamAV for unit tests (skip actual virus scan)
- Sample PDF files in test fixtures (valid, encrypted, corrupted, large)

**Mock services:**
- Mock Qdrant client for unit tests
- Mock embedding model for fast unit tests
- Mock ClamAV scanner for unit tests

**Test data:**
- Valid 10 MB PDF (benchmark processing time)
- Encrypted PDF (error handling)
- Corrupted PDF (error handling)
- 51 MB PDF (size validation)
- Non-PDF file (type validation)
- Empty PDF (content validation)

**Special considerations:**
- Async processing tests: need to wait for background task completion
- Rate limiting tests: verify 5 uploads/minute limit
- Virus scan tests: verify ClamAV integration (or mock for CI)

## Performance/Rate Limits

**From ExpectedLoad:**
- Upload frequency: 1-2 per day per instructor
- File size: 1-50 MB
- Processing time: < 30 seconds for 10 MB PDF (P95)

**Additional constraints from interview:**
- Rate limit: 5 uploads per minute per IP/user
- Prevent abuse while allowing bulk uploads for instructors

**Performance budget:**
- PDF parsing (10 MB): < 10 seconds
- Chunking: < 5 seconds
- Embedding generation (100 chunks): < 10 seconds
- Qdrant insertion (100 chunks): < 5 seconds
- Total: < 30 seconds

**Degradation strategy:**
- If processing time > 30s: queue document, notify user via status endpoint
- If Qdrant unavailable: queue insertion, retry with exponential backoff
- If embedding model fails: fallback to smaller model or queue for retry
