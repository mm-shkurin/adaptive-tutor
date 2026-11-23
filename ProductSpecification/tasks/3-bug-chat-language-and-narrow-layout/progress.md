# Task 3: Chat language and narrow layout -- Progress

Type: bug

## Spec
- [x] spec

## Fix: Russian replies + viewport scroll + narrow chat/source drawers

Cause and draft fix already known from live poke (HttpTutor English system prompts; `chat.css` `height: auto` under 960px; stacked side panels). Skip open-ended redesign — confirm then land.

- [ ] root cause analysis — confirm: (1) `_MODE_SYSTEM` / user content lack same-language rule; (2) narrow `.chat-layout` / `.chat-page` grow the document; (3) chat-side always in-flow on narrow. Record one-line RCA in spec if anything differs from working-tree draft
- [ ] design — Option A: land working-tree draft (prompt language line; `100dvh` chat-page; left/right drawers + toggles). Skip ADR
- [ ] steps discovery (scope: backend+frontend; expected inserts below — fold hazard GAPs or dismiss)

### Land language
- [ ] green-adapter tutor — `pytest backend/tests/test_http_tutor.py` green with same-language assertion
- [ ] refactor (cleanup) — only if green left a smell

### Land layout + drawers
- [ ] green-frontend — chat components/CSS; thread scrolls inside `.messages`
- [ ] green-selenium — `test_history_and_sources_reachable_on_narrow_window` (opens drawers via toggles)
- [ ] refactor (cleanup) — only if needed

### Account + branch backup
- [ ] progress — tick story 4 `## Next` UX items; point memory-bank / stories.md at merge-ready chat
- [ ] push — `git push -u origin HEAD` on `features/chat` (backup only; **do not** `*:dev`)
