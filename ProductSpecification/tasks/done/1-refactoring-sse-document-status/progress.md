# Task 1: SSE document status -- Progress

Type: refactoring

## Spec
- [x] spec

## Fix

### Step 1: Contract — SSE status stream in api-spec
- [x] api-spec (documents.yaml stream path, event shape, auth)
- [x] test-spec notes / UI expectation: poll no longer the happy path

### Step 2: Backend — emit status on transition
- [x] design (who publishes; lifecycle of the stream; reconnect)
- [x] green-adapter http (SSE endpoint + auth)
- [x] green-usecase / wiring (emit on waiting→indexing→ready|failed)
- [x] green-acceptance (upload → events without list poll)

### Step 3: Frontend — consume SSE, retire status poll
- [x] green-frontend (open stream while in flight; apply to rows)
- [x] green-frontend-api (event → page mapping)
- [x] align-design / green-selenium as needed for status pills
- [x] refactor (remove 250ms status poll happy path)
