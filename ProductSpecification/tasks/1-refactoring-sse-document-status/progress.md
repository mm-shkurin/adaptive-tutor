# Task 1: SSE document status -- Progress

Type: refactoring

## Spec
- [x] spec

## Fix

### Step 1: Contract — SSE status stream in api-spec
- [ ] api-spec (documents.yaml stream path, event shape, auth)
- [ ] test-spec notes / UI expectation: poll no longer the happy path

### Step 2: Backend — emit status on transition
- [ ] design (who publishes; lifecycle of the stream; reconnect)
- [ ] green-adapter http (SSE endpoint + auth)
- [ ] green-usecase / wiring (emit on waiting→indexing→ready|failed)
- [ ] green-acceptance (upload → events without list poll)

### Step 3: Frontend — consume SSE, retire status poll
- [ ] green-frontend (open stream while in flight; apply to rows)
- [ ] green-frontend-api (event → page mapping)
- [ ] align-design / green-selenium as needed for status pills
- [ ] refactor (remove 250ms status poll happy path)
