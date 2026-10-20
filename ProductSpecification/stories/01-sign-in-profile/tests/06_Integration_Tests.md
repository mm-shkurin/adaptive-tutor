# Sign in, landing, and profile — Integration Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with a Yandex confirmation through the fake provider, then each way Yandex can fail, then a retry that must not open a second account, then refresh.

## 1. Yandex

### 1.1 Yandex confirms the person and a session opens

Tier: 2

```gherkin
Given a guest
And the fake Yandex provider will confirm them
When the guest completes sign-in
Then one account exists
And the guest holds a session
And no live Yandex call was made
```

### 1.2 Yandex refuses and the guest stays signed out

Tier: 2 (hz-05)

```gherkin
Given a guest
And the fake Yandex provider refuses the sign-in
When the guest completes the return
Then the guest holds no session
And no account exists
```

### 1.3 Yandex times out and the guest stays signed out

Tier: 2 (hz-02, hz-05, hz-06)

```gherkin
Given a guest
And the fake Yandex provider does not answer before the deadline
When the guest completes the return
Then the guest holds no session
And no account exists
And the provider call is no longer running
```

### 1.4 Yandex returns an unreadable answer and the guest stays signed out

Tier: 2 (hz-02, hz-05)

```gherkin
Given a guest
And the fake Yandex provider returns an unreadable body
When the guest completes the return
Then the guest holds no session
And no account exists
```

### 1.5 A retry after a failed handoff does not open a second account

Tier: 2 (hz-02)

```gherkin
Given Yandex has already confirmed a person
And issuing that person's session then failed
When the same Yandex identity is confirmed again
Then one account exists
And the second confirmation does not open a second account
```

### 1.6 Refresh returns a new access token and the same refresh token

Tier: 2

```gherkin
Given a signed-in person
When the person refreshes their session
Then the new access token differs from the previous one
And the refresh token is the one they sent
And the new access token reads their profile
```

### 1.7 A Yandex server error is not retried

Tier: 2 (hz-02)

```gherkin
Given a guest
And the fake Yandex provider returns a server error
When the guest completes the return
Then the provider was called once
And the guest holds no session
And no account exists
```

### 1.8 A Yandex return cannot break the redirect

Tier: 2 (hz-05)

```gherkin
Given Yandex returns a code or an error that contains a line break
When the browser is sent back to the app
Then the redirect is a single location
And the line break is not a second header
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the fake Yandex provider` | `oauth_provider=fake`, no network call to Yandex |
| `completes sign-in` | Start, callback, then `POST /api/v1/auth/oauth/exchange` |
| `refuses the sign-in` | Provider error status on the code exchange |
| `does not answer before the deadline` | Provider call times out |
| `returns an unreadable body` | Provider body is not the token payload |
| `issuing that person's session then failed` | Identity stored, token issue failed; retry uses the same Yandex subject |
| `refreshes their session` | `POST /api/v1/auth/refresh` |
