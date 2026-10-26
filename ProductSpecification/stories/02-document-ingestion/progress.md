# Story 2: PDF-документы — Progress

## Spec
- [x] interview
- [x] story
- [x] mockups
- [x] api-spec
- [x] test-spec

Набор принят 2026-10-19: уровень 1 — 4, уровни 1+2 — 57, выше потолка. Не сокращать.

## Tier 1 — Backend Scenarios (01_API_Tests.md)

### 4.1 An accepted PDF becomes ready and its text and tables can be searched
- [x] red-acceptance
- [x] design
- [x] red-usecase
- [x] green-usecase
- [x] red-usecase (coverage: exact 500 tokens leaves no remainder)
- [x] green-usecase (coverage: exact 500 tokens leaves no remainder)
- [x] adapters-discovery (scope: storage, filestore, pdfreader, pieceindex, http; scanned all usecase ports; GAPs: storage missing → red-adapter storage / green-adapter storage, filestore missing → red-adapter filestore / green-adapter filestore, pdfreader missing → red-adapter pdfreader / green-adapter pdfreader, pieceindex missing → red-adapter pieceindex / green-adapter pieceindex, http missing → red-adapter http / green-adapter http)
- [x] red-adapter storage
- [x] green-adapter storage
- [x] red-adapter filestore
- [x] green-adapter filestore
- [x] red-adapter pdfreader
- [x] green-adapter pdfreader
- [S] red-adapter pieceindex (delivery without red/green; tests + impl together)
- [x] green-adapter pieceindex
- [S] red-adapter http (delivery without red/green; routes + wiring together)
- [x] green-adapter http
- [x] green-acceptance

## Tier 1 — Frontend Scenarios (02_UI_Tests.md)

### 1.1 An empty library shows the PDF door and no materials
- [x] red-selenium
- [x] red-frontend
- [x] green-frontend
- [S] red-frontend-api (empty document page is already the shape libraryView reads; doors and empty copy are presentational)
- [S] green-frontend-api (no API mapping to implement)
- [x] align-design
- [x] green-selenium
- [x] demo

### 1.2 A ready document shows its name, size, pages, and piece count
- [S] red-selenium (frontend-delivery without red/green; tests from test-spec with code)
- [S] red-frontend (frontend-delivery without red/green)
- [x] green-frontend
- [S] red-frontend-api (frontend-delivery without red/green)
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [S] demo (not in this delivery slice)

### 2.1 An accepted PDF appears as waiting and then becomes ready
- [S] red-selenium (frontend-delivery without red/green; tests from test-spec with code)
- [S] red-frontend (frontend-delivery without red/green)
- [x] green-frontend
- [S] red-frontend-api (frontend-delivery without red/green)
- [x] green-frontend-api
- [x] align-design
- [x] green-selenium
- [S] demo (not in this delivery slice)

## Harvest — Tier 1 → Tier 2

- [x] harvest

## Tier 2 — Backend Scenarios (01_API_Tests.md)

### 1.1 A person with no documents sees an empty list
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (GET /api/v1/documents + ListDocuments + DocumentIntake.list_page)

### 1.2 The list is this person's newest page
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (ListDocuments PAGE_SIZE=50 newest-first owner-scoped list_page)

### 1.3 A page read while a document arrives still covers each document once
- [x] red-acceptance
- [~] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 An unacceptable file adds no document
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.2 A file at either size edge is stored as that byte count
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (HTTP _MIN/_MAX_BYTES + SubmitDocument len(content) size_bytes)

### 2.3 A name of 255 characters is kept unchanged
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (HTTP documents._name() keeps <=255 unchanged)

### 2.4 A name that would split a letter at the limit is not stored broken
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.1 The same submission stored twice is one document
- [S] red-acceptance (delivery without red/green; HTTP + usecase together)
- [S] design (Idempotency-Key on DocumentIntake; unique per owner; replay skips rate)
- [S] red-usecase (delivery without red/green)
- [x] green-usecase
- [S] adapters-discovery (Memory + Postgres find_by_key/store; migration 0005)
- [x] green-acceptance (HTTP 200 replay / 201 create via TestClient)

### 3.2 Two overlapping copies of one submission store one document
- [S] red-acceptance (covered with 3.1–3.3 one-submission piece)
- [S] design (atomic claim; DuplicateSubmission → replay)
- [S] red-usecase (delivery without red/green)
- [x] green-usecase
- [S] adapters-discovery (same intake as 3.1)
- [x] green-acceptance (usecase race; HTTP covered by shared wiring)

### 3.3 Uploading the same PDF again creates another document
- [S] red-acceptance (covered with 3.1–3.3 one-submission piece)
- [S] design (new Idempotency-Key → new row even when bytes match)
- [S] red-usecase (delivery without red/green)
- [x] green-usecase
- [S] adapters-discovery (same intake as 3.1)
- [x] green-acceptance (HTTP TestClient)

### 4.2 A failed index names the part and leaves nothing searchable
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.3 A document whose indexing never started still finishes
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (AcceptanceServer._index_loop + IndexDocuments.index_waiting)

### 4.4 Three failed tries end as failed and the next document still indexes
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.5 Indexing that would store more than 2000 pieces fails the document
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.6 Indexing that has not finished in 5 minutes is failed
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.7 A finished document is not indexed again
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.8 A step that skips or reverses indexing is refused
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.9 An unknown status is not treated as ready
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.10 Two indexing claims of one document store one set of pieces
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.11 A second indexing run started while the first is going stores one set
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.12 A stale status write does not erase a newer one
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.13 A pathological PDF does not keep indexing busy past five minutes
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance
## Tier 2 — Integration Scenarios (06_Integration_Tests.md)

### 1.1 A clean PDF passes the virus check and becomes ready
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.2 A virus check that does not clear the file adds no document
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 A search store that does not accept the index fails the document
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.2 A retry after a partial index does not write the pieces twice
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.3 An embedding refusal stops, and a server error stays inside the three tries
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.4 Many indexes that fail together do not retry on the same tick
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.5 A call that finishes just before its deadline still counts
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance
## Tier 2 — Frontend Scenarios (02_UI_Tests.md)

### 0.1 A guest who opens documents sees no list
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 1.3 A list that is loading or that failed to load is not the empty library
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 2.2 A refused upload names the reason and leaves the list
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 2.3 A failed document shows the failure and the reason
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 2.4 A second press on one file adds one row
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 2.5 An older status arriving late does not replace a newer one
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 2.6 Leaving before the upload is accepted leaves the list unchanged
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 6.1 The presentation door does not upload a PDF
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

## Tier 2 — Security Scenarios (05_Security_Tests.md)

### 1.1 A hostile name and a hostile failure reason stay text
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 An upload cannot set the server's fields
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (POST /api/v1/documents file-only + Document.accepted + session owner)

### 2.2 A file name past 255 characters is refused
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (HTTP documents._name() name_too_long -> 400)

### 3.1 A missing document, a neighbour's document, and a guest's open look the same
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (ReadDocument owner-scoped get + DocumentNotFound 404)

### 3.2 A guest's list and upload match a missing document
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (documents._caller -> DocumentNotFound 404)

### 4.1 A sixth upload in the minute is refused and the five stay
- [S] red-acceptance (delivery without red/green; HTTP + usecase together)
- [S] design (UploadRateLimit port; fixed minute window in Redis/memory)
- [S] red-usecase (delivery without red/green)
- [x] green-usecase
- [S] adapters-discovery (RedisUploadRateLimit + MemoryUploadRateLimit; wired in SubmitDocument)
- [x] green-acceptance (HTTP 429 rate_limited via TestClient)

### 4.2 Two uploads that arrive together on the last free slot accept only one
- [S] red-acceptance (covered with 4.1–4.4 rate-limit piece)
- [S] design (atomic try_accept)
- [S] red-usecase (delivery without red/green)
- [x] green-usecase
- [S] adapters-discovery (same port as 4.1)
- [x] green-acceptance (usecase race; HTTP covered by shared wiring)

### 4.3 An upload at the start of the next minute is accepted
- [S] red-acceptance (covered with 4.1–4.4 rate-limit piece)
- [S] design (window key from clock minute)
- [S] red-usecase (delivery without red/green)
- [x] green-usecase
- [S] adapters-discovery (same port as 4.1)
- [x] green-acceptance (HTTP TestClient + clock advance)

### 4.4 An unreadable upload count refuses the upload
- [S] red-acceptance (covered with 4.1–4.4 rate-limit piece)
- [S] design (RedisError → rate_unavailable)
- [S] red-usecase (delivery without red/green)
- [x] green-usecase
- [S] adapters-discovery (same port as 4.1)
- [x] green-acceptance (HTTP 429 rate_unavailable via TestClient)

### 5.1 A failure echoes no secret, file text, stack, or path
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (http/errors.py sanitized JSON + InvalidDocument/rate handlers)
## Tier 2 — Load Scenarios (03_Load_Tests.md)

### 1.1 A lecture becomes ready within the indexing ceiling
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (SubmitDocument + ProbeIndexDocuments loop under 30s ceiling)

### 2.1 An upload during peak chat is answered before indexing finishes
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance
## Tier 2 — Infrastructure Scenarios (04_Infrastructure_Tests.md)

### 1.1 A dead document store refuses the upload and adds no document
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (MemoryDocumentIntake.dead -> StoreUnavailable -> 503)

### 1.2 The same person uploads after the store recovers
- [x] red-acceptance (harvest: already green)
- [S] design (harvest: covered by existing implementation)
- [S] red-usecase (harvest: covered by existing implementation)
- [S] green-usecase (harvest: covered by existing implementation)
- [S] adapters-discovery (harvest: covered by existing implementation)
- [S] green-acceptance (MemoryDocumentIntake.dead cleared; SubmitDocument + ReadDocument)

### 1.3 Repeated failed uploads return the store connections to baseline
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 The app refuses to start when indexing settings are missing
- [x] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance
