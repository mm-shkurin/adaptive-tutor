# Task 3: Chat language and narrow layout -- Progress

Type: bug

## Spec
- [x] spec

## Fix: Russian replies + viewport scroll + narrow chat/source drawers

Cause and draft fix already known from live poke (HttpTutor English system prompts; `chat.css` `height: auto` under 960px; stacked side panels). Skip open-ended redesign — confirm then land.

- [x] root cause analysis — confirmed against HEAD `5955ae6`: English-only `_MODE_SYSTEM`/`_user_content`; narrow `height: auto` + page min-height only; list always in-flow (`max-height: 180px`). Full write-up in `spec.md` §RCA. Live model reply not re-poked this session.
- [x] design — Option A: land working-tree draft (prompt language line; `100dvh` chat-page; left/right drawers + toggles). Skip ADR. Hazard scan hz-01…hz-08: no GAPs. Layout verified primarily via Selenium (narrow-window drawers + scroll ownership), not a manual poke.
- [x] steps discovery (scope: backend+frontend; inserts below; hazard GAPs none)

### Land language
- [ ] green-adapter tutor — `pytest backend/tests/test_http_tutor.py` green with same-language assertion
- [ ] refactor (cleanup) — only if green left a smell

### Land layout + drawers
- [ ] green-frontend — chat components/CSS; thread scrolls inside `.messages`
- [ ] green-selenium — `test_history_and_sources_reachable_on_narrow_window` (drawers via toggles + page does not grow / `.messages` owns overflow)
- [ ] refactor (cleanup) — only if needed

### Account + branch backup
- [ ] progress — tick story 4 `## Next` UX items; point memory-bank / stories.md at merge-ready chat
- [ ] push — `git push -u origin HEAD` on `features/chat` (backup only; **do not** `*:dev`)
