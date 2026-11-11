# Decision: Peak chat baseline holds in-flight messages

**Date**: 2026-11-11 **Scenarios**: Load 2.1

ExpectedLoad and the load DSL require one upload while 15 chat requests are
**in flight**, not after they have already returned.

| Rejected | Why |
|----------|-----|
| Instant 202 stub counted as accepted | PeakChatClient finished all 15 before the upload, so the baseline was never concurrent. |
| Defer the scenario until story 4 chat | The story already promises upload latency under peak chat; waiting leaves Load open for an unrelated feature. |

**Chosen**: Acceptance arms a `PeakChatHold` on `app.state`. The chat stub
awaits that hold so the 15 POSTs stay open. The baseline asserts
`hold.in_flight() == 15`, then uploads; release happens in the test finally.
Production without a hold still answers 202 immediately.
