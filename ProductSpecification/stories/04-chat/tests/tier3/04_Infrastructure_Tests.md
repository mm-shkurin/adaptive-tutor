# Chat — Infrastructure Tests (Tier 3)

## 3. Failure signal and redaction

### 3.1 A failed reply emits a signal a success does not

Tier: 3 (hz-07) — a missing failure signal does not change the thread the student sees; the kept person line, the absent tutor line, and the visible failure are already specified

```gherkin
Given a signed-in person with an askable chat
When the reply fails
Then a failure signal is recorded for that chat
And a successful reply does not record that signal
And the signal does not contain the document text
```
