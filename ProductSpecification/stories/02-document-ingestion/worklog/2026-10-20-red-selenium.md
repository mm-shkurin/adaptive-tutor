# red-selenium — 2026-10-20

Scenario: 1.1 An empty library shows the PDF door and no materials
Commits: `dcc15fc`, refactor `ffa161f`
The browser harness also sits in `276c0a3`: the shared index took the new acceptance files into the backend commit.

## Result

A signed-in browser opens the app root, stores the session, and clicks the visible «Документы» control. The screen is still the placeholder, so the test stays skipped.

First measured failure, before the locator change: `AssertionError`, message `assert 0 == 1`, missing `pdf-door-title`.
After `data-testid` locators: `TimeoutException`, message `no documents-tab`.
Skip reason: `RED: no documents-tab (TimeoutException)`.

## Tests

- Unskipped, link text: 1 failed (`assert 0 == 1`).
- Review, skipped: 1 skipped.
- Unskipped after locators: 1 failed (`TimeoutException: no documents-tab`).
- Refactor, skipped: 1 skipped, 0 failed.

## Log

The live `infrastructure/agent-progress.log` for this step was cleared before the next step, and `*.log` is gitignored. These lines are the run record, without invented clock times.

```
[red-agent] START: 1.1 empty library PDF door
[red-agent] PREDICT: AssertionError assert 0 == 1
[red-agent] RUN: 1 failed — assert 0 == 1
[red-agent] DONE: test skipped after predicted failure
[test-review-agent] START: test_empty_library_shows_the_pdf_door.py
[test-review-agent] FIX: tab and heading locators are data-testid
[test-review-agent] RUN: 1 skipped, 0 failed
[test-review-agent] DONE: skip reason is no documents-tab
[refactor-agent] START: document_library_statements.py
[refactor-agent] FIX: one WebDriverWait for tab and heading
[refactor-agent] RUN: 1 skipped, 0 failed
[refactor-agent] DONE: statements tightened
```
