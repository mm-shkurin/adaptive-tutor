# Task 2: Upload row and SSE status invisible until ready -- Progress

Type: bug

## Spec
- [x] spec

## Fix: upload row missing until ready; SSE status not visible live
- [x] root cause analysis — see spec.md § RCA (2026-11-12)
- [x] design — Option A (regression lock; keep 6f0f417/d7987ee); Skip ADR
- [x] steps discovery (scope: frontend; scanned all _index.md groups; GAPs: hz-02 folded as red-frontend (dup status apply + stream-open classification); hz-03 folded as red-frontend (status-rank / fresherPage already + reverse-order assert); hz-05 dismissed: no auth/HTML change in this fix; hz-06 folded as red-frontend (FALLBACK_POLL_LIMIT cap); hz-07 folded as red-frontend (UPLOAD_TIMEOUT_MS vs virus budget); hz-08 folded as red-frontend (createSubmission one-POST + stream helpers); hz-01/hz-04 none fired)
- [~] red-frontend — lock Pass helpers: timeout budget, STREAM_BASE resolve, isStreamOpenError, status apply idempotency, fallback poll cap
- [ ] green-frontend
- [ ] green-selenium — verification only: TestUploadAppearsWaitingThenReady (hold indexing; existing Pass criteria)
- [ ] demo — TestUploadAppearsWaitingThenReady
