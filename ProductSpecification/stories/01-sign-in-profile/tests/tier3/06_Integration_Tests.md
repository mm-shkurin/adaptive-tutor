# Sign in, landing, and profile — Integration Tests (Tier 3)

## 1. Yandex

### 1.9 A Yandex failure is recorded and a success is not

Tier: 3 (hz-07) — a missing failure record does not change what the guest sees; signed-out and the visible failure are already specified

```gherkin
Given a guest
When Yandex refuses, times out, or returns an unreadable answer
Then that failure is recorded without the email and without a token
And a later successful sign-in is not recorded as a failure
```
