# Quizzes — Infrastructure Tests (Tier 3)

## 3. Failure signal and redaction

### 3.2 A successful create does not record the failure signal

Tier: 3 (hz-07) — a false failure signal does not change the quiz the student receives; the stored quiz and the visible take are already specified

```gherkin
Given a signed-in person with a ready PDF
And the completions fake returns a valid quiz
When the person creates a quiz
Then the quiz is stored
And the failure signal is not recorded
```
