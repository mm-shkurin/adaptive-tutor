# Sign in, landing, and profile — API Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with a Yandex sign-in that opens one account, then read the profile, then refuse a bad name before keeping a good one, then the photo, then sign-out and delete.

## 1. Sign-in

### 1.1 Yandex confirms the person and opens one session

Tier: 1

```gherkin
Given a guest with no account
When the guest completes sign-in with Yandex
Then one account exists for that Yandex identity
And the guest holds a session for that account
```

### 1.2 The same Yandex return played twice opens one account

Tier: 2 (hz-02)

```gherkin
Given a guest with no account
When the same Yandex return is delivered twice
Then one account exists for that Yandex identity
And the second delivery does not open a second account
And the second delivery does not open a second session
```

### 1.3 An expired Yandex return opens no session

Tier: 2 (hz-05)

```gherkin
Given a guest with no account
And the return from Yandex has expired
When the guest completes that return
Then no account exists
And the guest holds no session
```

### 1.4 Two overlapping first sign-ins open one account

Tier: 2 (hz-03)

```gherkin
Given two first sign-ins for the same Yandex identity pass the existence check together
When both sign-ins complete
Then one account exists for that Yandex identity
And the second writer does not create a second account
```

### 1.5 A foreign handoff code is refused like an unknown one

Tier: 2 (hz-05)

```gherkin
Given a handoff code issued for someone else, a code that was never issued, and an expired code
When each code is exchanged
Then all three refusals match
And none of them opens an account
```

### 1.6 A Yandex return is accepted only before it expires

Tier: 2 (hz-07)

```gherkin
Given a fixed clock and a Yandex return with an expiry
When the return is completed just before expiry, at expiry, and just after
Then only the return completed just before expiry opens a session
And the return at expiry opens no session
And the return just after expiry opens no session
```

### 1.7 An exchange cannot set the account's id, email, or role

Tier: 2 (hz-05)

```gherkin
Given a guest exchanging a valid Yandex code
When the exchange also carries an id, an email, and a role
Then the account id is the one the server assigned
And the email is the Yandex email
And no role is stored
```

---

## 2. Read profile

### 2.1 The signed-in person reads their own profile

Tier: 1

```gherkin
Given a signed-in person with a name, a Yandex email, a photo, and a registration instant
When the person reads their profile
Then the profile shows that name
And the profile shows that Yandex email
And the profile shows that photo
And the profile shows that registration instant
```

### 2.2 A name of sixty multibyte letters round-trips unchanged

Tier: 2 (hz-01)

```gherkin
Given a signed-in person
When the person saves a name of sixty Cyrillic letters
Then the stored name equals those sixty letters
And reading the profile returns those same sixty letters
```

---

## 3. Rename

### 3.1 An invalid name is refused

Tier: 2 (hz-06, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person with a saved name and a photo
When the person <submits>
Then the rename is refused
And the saved name is unchanged
And the photo is unchanged

Examples:
  | submits |
  | submits a name of sixty-one characters |
  | submits a name made only of spaces |
  | submits a null name |
```

### 3.3 A name that would split a letter at the limit is not stored broken

Tier: 2 (hz-01)

```gherkin
Given a signed-in person
When the person submits a name whose sixtieth place falls inside one letter
Then the stored name is either unchanged or a whole-letter name
And the stored name contains no broken letter
```

### 3.4 A rename that omits the name leaves the current name

Tier: 2 (hz-05)

```gherkin
Given a signed-in person with a saved name and a photo
When the person submits a rename that omits the name
Then the saved name is unchanged
And the photo is unchanged
```

### 3.6 An empty name restores the Yandex name

Tier: 2 (hz-05)

```gherkin
Given a signed-in person whose saved name differs from the Yandex name and who has a photo
When the person submits an empty name
Then the profile name is the Yandex name
And the photo is unchanged
```

### 3.7 A name of sixty characters is kept and the email and date stay

Tier: 1 (hz-05)

```gherkin
Given a signed-in person with a Yandex email, a registration instant, and a photo
When the person saves a name of sixty characters
Then the profile name is those sixty characters
And the Yandex email is unchanged
And the registration instant is unchanged
And the photo is unchanged
```

### 3.8 Two saves in a row leave the last accepted name

Tier: 2

```gherkin
Given a signed-in person
When the person saves one name and then saves a different name
Then the profile shows the second name
And the profile shows that name only once
```

---

## 4. Photo

### 4.1 An invalid photo is refused

Tier: 2 (hz-05, hz-06)

```gherkin
Scenario Outline:
Given a signed-in person with a photo
When the person submits <photo>
Then the upload is refused
And the previous photo stays
And <discarded>

Examples:
  | photo | discarded |
  | a photo of another kind | the previous photo stays |
  | a photo larger than ten megabytes | the oversized file is not kept |
```

### 4.3 An allowed photo replaces the previous one

Tier: 1

```gherkin
Given a signed-in person with a photo
When the person submits a jpeg, png, or webp photo within ten megabytes
Then the profile shows the new photo
And the previous photo is no longer the profile photo
```

### 4.4 Removing the photo leaves the profile without one

Tier: 2

```gherkin
Given a signed-in person with a photo
When the person removes the photo
Then the profile has no photo
```

### 4.5 Replacing a photo leaves the neighbour's photo

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with a photo and a neighbour with their own photo
When the person replaces their photo
Then the neighbour's photo is unchanged
```

### 4.6 Removing a photo leaves the neighbour's photo

Tier: 2 (hz-04)

```gherkin
Given a signed-in person with a photo and a neighbour with their own photo
When the person removes their photo
Then the neighbour's photo is unchanged
```

---

## 5. Sign-out and delete

### 5.1 Sign-out revokes the session

Tier: 1

```gherkin
Given a signed-in person with a session
When the person signs out
Then that session can no longer read the profile
And that session can no longer change the profile
```

### 5.2 A second sign-out with the same session still reports signed out

Tier: 2 (hz-02)

```gherkin
Given a person who has already signed out
When the same session signs out again
Then the sign-out is accepted
And the profile stays unchanged
```

### 5.3 Delete removes only this account

Tier: 1 (hz-04, hz-05)

```gherkin
Given a signed-in person and a neighbour with their own name
When the person deletes their account
Then the person's account is gone
And the neighbour's name is unchanged
And the person's session can no longer read a profile
```

### 5.4 The same Yandex identity after delete is a new account

Tier: 2

```gherkin
Given a person whose account was deleted
When that Yandex identity signs in again
Then a new account exists
And the new account is not the deleted one
```

### 5.5 A deleted session and an unknown session get the same refusal

Tier: 2 (hz-05, hz-07)

```gherkin
Given a deleted person's former session and a session that was never issued
When each asks for the profile
Then both refusals match
And neither refusal names an account, a token, or an email
```

### 5.6 Two deletes in a row leave the account gone once

Tier: 2 (hz-02, hz-05)

```gherkin
Given a signed-in person
When the person deletes their account twice
Then the account is gone
And the second delete does not remove the neighbour
And the second delete is the same refusal as an unknown session
```

### 5.7 A delete with no session removes no account

Tier: 2 (hz-04)

```gherkin
Given two accounts
When a delete is attempted with no session
Then both accounts remain
```

### 5.8 A deleted session and an unknown session match on rename, photo, and refresh

Tier: 2 (hz-05)

```gherkin
Given a deleted person's former session and a session that was never issued
When each tries to rename, to replace the photo, to remove the photo, and to refresh
Then each pair of refusals matches
And no account changes
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `a guest with no account` | No user row and no bearer token |
| `completes sign-in with Yandex` | Fake OAuth provider, then `POST /api/v1/auth/oauth/exchange` |
| `the same Yandex return is delivered twice` | One handoff code posted to exchange twice |
| `the return from Yandex has expired` | Exchange of a spent or expired handoff code returns 401 |
| `reads their profile` | `GET /api/v1/user/profile` |
| `saves a name` / `submits a name` | `PATCH /api/v1/user/profile` with `{name}` |
| `submits a rename that omits the name` | `PATCH` body `{}` |
| `submits a null name` | `PATCH` body `{name: null}` |
| `submits an empty name` | `PATCH` body `{name: ""}` |
| `submits a photo` | `PUT /api/v1/user/avatar` multipart field `file` |
| `removes the photo` | `DELETE /api/v1/user/avatar` |
| `signs out` | `POST /api/v1/auth/logout` with the refresh token |
| `deletes their account` | `DELETE /api/v1/user` with no body |
| `both refusals match` | Same status and same error code, no email and no token in the body |
