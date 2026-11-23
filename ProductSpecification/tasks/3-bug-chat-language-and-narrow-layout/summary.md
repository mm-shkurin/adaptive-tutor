# Task 3 journey

## green-selenium (2026-11-23)

**Decision:** Treat Selenium `test_history_and_sources_reachable_on_narrow_window` as the layout gate (drawers + page height / overflow ownership), not a live browser poke; language stays a unit assert on the HttpTutor system and user messages.
**Why:** Acceptance already boots its own API + Vite; a live `:8010`/`:5174` poke is optional and model language compliance is intermittent.
**Where applied:** `acceptance/statements/chat_screen_statements.py`, `backend/tests/test_http_tutor.py`
