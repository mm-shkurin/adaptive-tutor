# Presentations — Security Tests

## 1. Authorization

### 1.1 Foreign presentation id is absent on every mutating verb

Tier: 1 (sec:IDOR, hz-05)

```gherkin
Scenario Outline:
Given a signed-in person
And a neighbour's presentation id
When the person <verb> that id
Then the refusal matches a missing presentation
And the neighbour's data is unchanged

Examples:
  | verb |
  | GET |
  | PATCH |
  | POST slides |
  | DELETE slide |
  | POST index |
  | DELETE |
```

### 1.2 Mass assignment cannot set status or piece_count on create

Tier: 1 (sec:MassAssignment, hz-05)

```gherkin
Given a signed-in person
When the person creates a presentation with body fields status ready and piece_count 9
Then the stored presentation is draft
And piece_count is null
And status is not ready
```

### 1.3 Error bodies never include image bytes or paths

Tier: 2 (sec:Disclosure, hz-07)

```gherkin
Given a signed-in person with a draft
And the virus check fails
When the person adds a jpeg named with a path-like string
Then the error message has no file bytes, no absolute path, and no stack
```

### 1.4 Progress material filter cannot read a neighbour's mastery

Tier: 1 (sec:IDOR, hz-05)

```gherkin
Given a signed-in person
And a neighbour material with topics
When the person reads progress filtered by that material
Then the refusal matches progress_not_found
And no topic from the neighbour is returned
```
