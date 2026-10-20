# Sign in, landing, and profile — UI Tests

> **Implementation Order**: Tests are numbered for sequential TDD implementation.
> Start with the landing a guest can read, then the profile they see after Yandex, then name, photo, and theme, then the delete gate and sign-out.

## 1. Landing

### 1.1 A guest sees the AdaptiveTutor landing and one Yandex door

Tier: 1

```gherkin
Given a guest
When the guest opens the landing
Then the landing shows the AdaptiveTutor hero and the four feature cards
And the only sign-in door is Yandex
And no email-and-password door is shown
And no guest door is shown
```

### 1.2 The guest starts sign-in and sees the waiting state

Tier: 2 (hz-08)

```gherkin
Given a guest on the landing
When the guest chooses sign in with Yandex
Then the guest sees that Yandex is being asked
And no profile is shown
```

### 1.3 A double press on sign-in starts one sign-in

Tier: 2 (hz-08)

```gherkin
Given a guest on the landing
When the guest presses sign in twice before Yandex answers
Then one sign-in starts
And the guest sees the waiting state
```

---

## 2. Profile display

### 2.1 The profile shows the person, the student line, and the photo

Tier: 1

```gherkin
Given a signed-in person with a name, a Yandex email, a photo, and a registration instant
When the person opens their profile
Then the profile shows that name
And the profile shows that Yandex email
And the profile shows «Роль: Студент · ОмГТУ»
And the profile shows the photo
And the university is not a choice
```

### 2.2 The registration day is the local calendar day

Tier: 2 (hz-07)

```gherkin
Given a signed-in person whose registration instant is 23:30 in their local zone on a day that is already the next day in UTC
When the person opens their profile
Then the profile shows the local calendar day
And the profile does not show the UTC day
```

### 2.3 Without a photo the initials show

Tier: 2 (hz-08)

```gherkin
Given a signed-in person with no photo
When the person opens their profile
Then the profile shows the person's initials
And remove-photo is absent
```

### 2.4 A profile that fails to load shows an error with a retry

Tier: 2 (hz-08)

```gherkin
Given a signed-in person
And the profile cannot be loaded
When the person opens their profile
Then the person sees an error and a retry
And the error is not a spinner
And the profile fields are not shown
```

---

## 3. Name, photo, and theme

### 3.1 Saving a name shows the saved name

Tier: 1

```gherkin
Given a signed-in person editing their name
When the person saves a name within sixty characters
Then the profile shows that name
And the email, the student line, and the registration day stay
```

### 3.2 Clearing the name shows the Yandex name

Tier: 2

```gherkin
Given a signed-in person whose saved name differs from the Yandex name
When the person clears the name and saves
Then the profile shows the Yandex name
```

### 3.3 A theme choice stays on this device and is painted before the first screen

Tier: 2

```gherkin
Given a signed-in person
When the person picks light, dark, or system
Then the next first screen is painted in that choice
And the choice is still there after the browser reopens
And the profile on the server is unchanged
```

### 3.4 Leaving an unsaved name keeps the saved name

Tier: 2

```gherkin
Given a signed-in person who has typed a new name and not saved it
When the person leaves the profile and opens it again
Then the profile shows the saved name
And the typed name is gone
```

### 3.5 A double press on save sends one rename

Tier: 2 (hz-08)

```gherkin
Given a signed-in person editing their name
When the person presses save twice before the first answer returns
Then the server receives one rename
And the profile shows that name once
```

### 3.6 A late older save does not replace the newer name

Tier: 2 (hz-08)

```gherkin
Given a signed-in person who saved a newer name after an older save was still in flight
When the older save's answer arrives after the newer one
Then the profile keeps showing the newer name
```

### 3.7 A refused save puts the previous name back

Tier: 2 (hz-08)

```gherkin
Given a signed-in person who has typed a name the server will refuse
When the person saves and the server refuses
Then the profile shows the name from before the edit
```

### 3.8 An unknown theme value paints the system theme

Tier: 2 (hz-05)

```gherkin
Given this device holds a theme value other than system, light, or dark
When the first screen is painted
Then the screen uses the system theme
```

---

## 4. Delete and sign-out

### 4.1 Delete stays off until the typed email matches

Tier: 1

```gherkin
Given a signed-in person with the delete dialog open
When the typed email differs from the account email
Then delete is disabled
And no delete is sent
When the typed email equals the account email
Then delete is enabled
```

### 4.2 A matching email deletes the account

Tier: 1

```gherkin
Given a signed-in person who typed their account email
When the person confirms delete
Then the account is gone
And the guest sees that the account was deleted
```

### 4.3 A double press on delete removes the account once

Tier: 2 (hz-08)

```gherkin
Given a signed-in person who typed their account email
When the person confirms delete twice before the first answer returns
Then the server receives one delete
And the guest sees that the account was deleted
```

### 4.4 Sign-out returns the guest to the landing

Tier: 1

```gherkin
Given a signed-in person on their profile
When the person signs out
Then the guest sees the landing
And the profile is not shown
```

### 4.5 Yandex failure leaves a visible failure and no session

Tier: 2 (hz-08)

```gherkin
Given a guest waiting on Yandex
When Yandex fails
Then the guest sees a visible failure
And the failure offers a retry and is not a spinner
And the guest holds no session
And the profile is not shown
```

### 4.6 A double press on sign-out sends one sign-out

Tier: 2 (hz-08)

```gherkin
Given a signed-in person on their profile
When the person presses sign out twice before the first answer returns
Then the server receives one sign-out
And the guest sees the landing
```

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `opens the landing` | Guest route, mockup hero and four cards |
| `chooses sign in with Yandex` | The only door, label «Войти через Яндекс» |
| `opens their profile` | Profile screen after a session exists |
| `«Роль: Студент · ОмГТУ»` | Fixed text, not a field |
| `the local calendar day` | `created_at` rendered in the device zone |
| `picks light, dark, or system` | Device storage under this product's theme key |
| `presses save twice` | One `PATCH /api/v1/user/profile` |
| `delete is disabled` | Danger button disabled until the input equals `email` |
| `confirms delete` | Enabled button sends `DELETE /api/v1/user` |
| `signs out` | «Выйти», then the landing |
| `Yandex fails` | Return screen with no session |
