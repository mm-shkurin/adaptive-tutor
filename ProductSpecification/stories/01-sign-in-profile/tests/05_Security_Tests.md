# Sign in, landing, and profile — Security Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with a name that must stay text, then fields the person must not be able to write, then a session that must stay dead.

## 1. Name as text

### 1.1 A hostile name stays text

Tier: 2 (sec:SQLi, sec:XSS, hz-05)

```gherkin
Given a signed-in person and a neighbour
When the person saves a name containing query metacharacters and markup
Then the profile name is that text
And the person's account is unchanged apart from the name
And the neighbour's account is unchanged
And the profile shows that name as text
And the markup is not treated as a control
```

---

## 2. Fields the person does not own

### 2.1 A rename cannot write the email, the date, or a role

Tier: 2 (sec:MassAssignment, hz-05)

```gherkin
Given a signed-in person with a Yandex email, a registration instant, a photo, and an account id
When the person submits a rename that also carries an email, a registration instant, a role, an id, an owner, and a photo link
Then the profile name changes only if the name itself is acceptable
And the Yandex email is unchanged
And the registration instant is unchanged
And the account id is unchanged
And the owner is unchanged
And the photo is unchanged
And no role is stored
```

### 2.2 A name past sixty characters is refused

Tier: 2 (sec:InputLength, hz-06)

```gherkin
Given a signed-in person with a saved name
When the person submits a name of sixty-one characters
Then the rename is refused
And the saved name is unchanged
```

---

## 3. Session

### 3.1 A revoked session cannot refresh or read the profile

Tier: 2 (sec:JWT)

```gherkin
Given a person who has signed out
When that session asks to refresh
Then the refresh is refused
When that session asks for the profile
Then the read is refused
And neither refusal contains the token
```

### 3.2 An access token presented as a refresh token is refused

Tier: 2 (sec:JWT, hz-05)

```gherkin
Given a signed-in person
When the person presents their access token as a refresh token
Then the refresh is refused
And the session still reads the profile
```

### 3.3 A failure never echoes the token or the email

Tier: 2 (hz-07)

```gherkin
Given a signed-in person with a known token and a known Yandex email
When sign-in fails, a rename is refused, a photo is refused, and delete is refused
Then none of those answers contain the token
And none of those answers contain the email
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `query metacharacters` | A name containing `' OR 1=1` stored via parameterized write |
| `markup` | A name containing `<script>` rendered as text |
| `also carries an email, a registration instant, and a role` | Extra JSON keys on `PATCH /api/v1/user/profile`; `additionalProperties` is false for unknown keys, and `email`, `created_at`, and `role` are not writable |
| `asks to refresh` | `POST /api/v1/auth/refresh` |
| `presents their access token as a refresh token` | Refresh body holds the access token |
| `none of those answers contain the token` | Error body matches the error schema and has no token and no email |
