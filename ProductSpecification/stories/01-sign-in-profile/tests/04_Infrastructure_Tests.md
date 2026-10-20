# Sign in, landing, and profile — Infrastructure Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with a dead account store, then its recovery, then a boot that refuses to start without Yandex settings.

## 1. Account store

### 1.1 A dead account store refuses the profile

Tier: 2 (hz-05)

```gherkin
Given a signed-in person
And the account store is unreachable
When the person reads their profile
Then the read is refused
And no empty profile is returned
When the person saves a name
Then the rename is refused
And the stored name is unchanged
```

### 1.2 The same person reads their profile after the store recovers

Tier: 2

```gherkin
Given a signed-in person
And the account store was unreachable and is reachable again
When the person reads their profile
Then the profile shows their name, email, and registration instant
```

### 1.3 Repeated failed reads return the store connections to baseline

Tier: 2 (hz-06)

```gherkin
Given a signed-in person
When the person reads their profile many times while the account store is refusing
Then the live store connections return to the baseline
And a later successful read still returns their profile
```

---

## 2. Startup

### 2.1 The app refuses to start when Yandex settings are missing

Tier: 2 (hz-05, hz-07)

```gherkin
Given the Yandex client settings are unset
When the app starts
Then startup fails before it accepts a guest
And the app does not offer a guest door in their place
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the account store is unreachable` | Postgres connection fails on profile read and rename |
| `the read is refused` | Error response, not a 200 with an empty profile |
| `Yandex client settings are unset` | Client id and secret absent at process start |
| `startup fails` | Process exits on boot instead of serving sign-in |
