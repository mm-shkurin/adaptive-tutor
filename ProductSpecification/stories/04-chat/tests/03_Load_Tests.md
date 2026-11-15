# Chat — Load Tests

Latency profile. `ProductSpecification/ExpectedLoad.md` sets the chat reply at P95 under 3 seconds and P99 under 5 seconds, and the burst this story must hold is 20 people sending 5 replies in one minute. The upload while 15 chat accepts are held is already covered by story 2 and is not repeated here.

---

## 1. Reply latency at the declared burst

### 1.1 A chat reply under the peak burst stays inside the latency budget

Tier: 2

```gherkin
Given the chat latency baseline
And each person has an askable chat
When the peak burst sends
Then each reply arrives whole
And the replies stay inside the chat latency budget
And a failed fake is counted as a failed reply, not as a hung send
```

Threshold: P95 under 3 seconds, P99 under 5 seconds, at 20 people × 5 sends in one minute. Catches a reply path that waits on an uncapped search or an inner timeout longer than the budget.

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `the chat latency baseline` | `ProductSpecification/ExpectedLoad.md` chat row. Model, embeddings, and the search store are the story's fakes, not live services |
| `the peak burst sends` | 20 signed-in people, 5 `POST /api/v1/chats/{id}/messages` each, started within one minute |
| `the chat latency budget` | P95 < 3s and P99 < 5s measured on the student send, end to end through the fakes |
| `a failed fake is counted as a failed reply` | The fake returns `reply_failed` inside the budget. The request does not stay open |
