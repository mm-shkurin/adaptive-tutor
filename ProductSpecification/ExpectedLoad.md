# Expected Load — AdaptiveTutor

## Load Challenge Profile

**Primary user context:** University/college students working on course materials during peak hours (before exams, assignment deadlines).

## Target Load (MVP)

### Concurrent Users
- **Peak:** 50 concurrent students
- **Average:** 10-20 concurrent students
- **Growth path:** 200+ concurrent users (v2)

### Request Patterns

#### Chat Endpoint
- **Frequency:** 1-3 requests per minute per active user
- **Peak burst:** 5-10 requests per minute (intensive Q&A)
- **Latency SLA:** P95 < 3 seconds (end-to-end: retrieval + LLM generation)

#### Document Upload
- **Frequency:** 1-2 uploads per day per instructor
- **File size:** 1-50 MB per document
- **Processing time:** < 30 seconds for 10 MB PDF (indexing + embedding)

#### Quiz Generation
- **Frequency:** 1 per topic per session
- **Latency SLA:** P95 < 5 seconds

### Storage

#### Vector Database
- **Initial:** 10,000 chunks (100 documents × 100 chunks each)
- **Growth:** 100,000+ chunks (v2)
- **Embedding dimension:** 1536 (OpenAI) or 768 (local models)

#### PostgreSQL
- **Students:** 100-500
- **Documents:** 100-500
- **Chat sessions:** 1,000-5,000
- **Quiz records:** 500-2,000

## Load Test Scenarios

### Tier 1 (Critical Path)
1. **Concurrent chat queries** — 20 users × 5 requests each within 1 minute
2. **Document upload during peak chat** — 1 upload while 15 concurrent chat requests active
3. **Quiz generation** — 5 concurrent quiz requests

### Tier 2 (Edge Cases)
1. **Large document upload** — 50 MB PDF during peak chat
2. **Rapid consecutive queries** — 10 requests from single user within 30 seconds
3. **Failed LLM API retry** — LLM timeout → retry → fallback

### Tier 3 (Stress)
1. **Sustained load** — 50 concurrent users over 10 minutes
2. **Vector DB hot path** — 1000 retrieval queries within 30 seconds
3. **Database connection pool exhaustion** — 100 concurrent DB operations

## Infrastructure Constraints

- **LLM API rate limits:** OpenAI Tier 1 (3,000 RPM, 200,000 TPM) or local LLM (Ollama/vLLM)
- **Vector DB:** Pinecone (Serverless) or Qdrant (self-hosted, Docker)
- **Database:** PostgreSQL 15+ with connection pooling (PgBouncer)
- **Storage:** S3-compatible or local filesystem (MVP: local)

## Performance Budget

| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| Chat query (retrieval + LLM) | 1.5s | 3s | 5s |
| Document indexing (10 MB) | 15s | 25s | 40s |
| Quiz generation | 2s | 5s | 8s |
| Vector search (top-10) | 200ms | 500ms | 1s |
| PostgreSQL query | 50ms | 150ms | 300ms |

## Degradation Strategy

When P95 SLA breached:
1. **Cache retrieval results** — Redis with 5-minute TTL
2. **Reduce context window** — top-5 chunks instead of top-10
3. **Fallback to faster LLM** — GPT-3.5 instead of GPT-4
4. **Queue non-critical operations** — document indexing, quiz generation
