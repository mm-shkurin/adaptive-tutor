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
- [ ] green-adapter storage
- [ ] red-adapter filestore
- [ ] green-adapter filestore
- [ ] red-adapter pdfreader
- [ ] green-adapter pdfreader
- [ ] red-adapter pieceindex
- [ ] green-adapter pieceindex
- [ ] red-adapter http
- [ ] green-adapter http
- [ ] green-acceptance

## Tier 1 — Frontend Scenarios (02_UI_Tests.md)

### 1.1 An empty library shows the PDF door and no materials
- [x] red-selenium
- [x] red-frontend
- [x] green-frontend
- [S] red-frontend-api (empty document page is already the shape libraryView reads; doors and empty copy are presentational)
- [S] green-frontend-api (no API mapping to implement)
- [~] align-design
- [ ] green-selenium
- [ ] demo

### 1.2 A ready document shows its name, size, pages, and piece count
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

### 2.1 An accepted PDF appears as waiting and then becomes ready
- [ ] red-selenium
- [ ] red-frontend
- [ ] green-frontend
- [ ] red-frontend-api
- [ ] green-frontend-api
- [ ] align-design
- [ ] green-selenium
- [ ] demo

## Harvest — Tier 1 → Tier 2

- [ ] harvest

## Tier 2 — Backend Scenarios (01_API_Tests.md)

### 1.1 A person with no documents sees an empty list
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.2 The list is this person's newest page
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.3 A page read while a document arrives still covers each document once
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 An unacceptable file adds no document
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.2 A file at either size edge is stored as that byte count
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.3 A name of 255 characters is kept unchanged
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.4 A name that would split a letter at the limit is not stored broken
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.1 The same submission stored twice is one document
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.2 Two overlapping copies of one submission store one document
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.3 Uploading the same PDF again creates another document
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.2 A failed index names the part and leaves nothing searchable
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.3 A document whose indexing never started still finishes
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.4 Three failed tries end as failed and the next document still indexes
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.5 Indexing that would store more than 2000 pieces fails the document
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.6 Indexing that has not finished in 5 minutes is failed
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.7 A finished document is not indexed again
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.8 A step that skips or reverses indexing is refused
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.9 An unknown status is not treated as ready
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.10 Two indexing claims of one document store one set of pieces
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.11 A second indexing run started while the first is going stores one set
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.12 A stale status write does not erase a newer one
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.13 A pathological PDF does not keep indexing busy past five minutes
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

## Tier 2 — Integration Scenarios (06_Integration_Tests.md)

### 1.1 A clean PDF passes the virus check and becomes ready
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.2 A virus check that does not clear the file adds no document
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 A search store that does not accept the index fails the document
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.2 A retry after a partial index does not write the pieces twice
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.3 An embedding refusal stops, and a server error stays inside the three tries
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.4 Many indexes that fail together do not retry on the same tick
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.5 A call that finishes just before its deadline still counts
- [ ] red-acceptance
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
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 An upload cannot set the server's fields
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.2 A file name past 255 characters is refused
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.1 A missing document, a neighbour's document, and a guest's open look the same
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 3.2 A guest's list and upload match a missing document
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.1 A sixth upload in the minute is refused and the five stay
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.2 Two uploads that arrive together on the last free slot accept only one
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.3 An upload at the start of the next minute is accepted
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 4.4 An unreadable upload count refuses the upload
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 5.1 A failure echoes no secret, file text, stack, or path
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

## Tier 2 — Load Scenarios (03_Load_Tests.md)

### 1.1 A lecture becomes ready within the indexing ceiling
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 An upload during peak chat is answered before indexing finishes
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

## Tier 2 — Infrastructure Scenarios (04_Infrastructure_Tests.md)

### 1.1 A dead document store refuses the upload and adds no document
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.2 The same person uploads after the store recovers
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 1.3 Repeated failed uploads return the store connections to baseline
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance

### 2.1 The app refuses to start when indexing settings are missing
- [ ] red-acceptance
- [ ] design
- [ ] red-usecase
- [ ] green-usecase
- [ ] adapters-discovery
- [ ] green-acceptance
