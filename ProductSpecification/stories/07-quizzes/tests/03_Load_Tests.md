# Quizzes — Load Tests

Latency is the project's declared challenge in `ProductSpecification/ExpectedLoad.md`. That document's quiz rows — 5 concurrent generations and P95 under 5 seconds — were written for another stack. The interview set no new ceiling: create is one synchronous completions call, the same shape as a chat send, with no queue and no new rate.

This file records that decision. It adds no scenario and no numeric ceiling. A passing green path is the completions fake in the API and integration specs, not a live freellmapi timing run.

---

## DSL Technical Reference

| DSL Statement | Technical Implementation |
|---------------|-------------------------|
| `no new ceiling` | Do not assert `ExpectedLoad.md`'s quiz P95 of 5 seconds or its "5 concurrent quiz requests" row from this story. Chat send keeps its own latency budget in story 4 |
| `one synchronous completions call` | `POST /api/v1/quizzes` waits on one fake completions response. There is no quiz queue and no retry loop |
