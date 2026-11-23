# Task 3: Chat language and narrow layout

Type: bug

## Problem

On the live chat screen (`features/chat`, Vite `:5174` + API `:8010`, freellmapi chat, fake OAuth) three UX failures block story-4 close:

1. **Reply language.** Person asks in Russian; tutor sometimes replies in English. System prompts in `HttpTutor` were English-only and did not require matching the question language.
2. **Page scroll.** On a narrow window (≤960px) the chat layout used `height: auto`, so the thread grew the whole document. To read earlier lines the person had to scroll the browser tab to the top; `.messages` did not own the scroll.
3. **Chat list placement.** On the same narrow width the history sat as a short strip above the thread (`aside.chat-side`, ~140px). The person wants it as a left drawer opened on demand (chat-list pattern), not a permanent top strip. Sources should mirror that (right drawer) so the thread keeps full height.

**Environment:** local poke — backend `:8010`, frontend `:5174`, `OAUTH_PROVIDER=fake`, `FREE_LLM_CHAT_URL` → freellmapi.

**Frequency:** language — intermittent per model; layout — every narrow viewport.

**Working tree (already drafted, not committed):** language guard in `backend/adapters/tutor/http_tutor.py` + unit test; viewport lock + drawers in `frontend/src/styles/chat.css` and chat components; Selenium statement updates for drawer open. AFK should verify and land these, not rediscover from zero.

## Reproduction

1. Sign in (fake OAuth), open Чат with a ready PDF that has vectors.
2. Send a short Russian question. **Fail:** tutor answer in English.
3. Resize to ~800–880px wide with a long thread. **Fail:** document/page scroll grows; chat list is a top strip.
4. **Pass for this task:** Russian question → Russian reply; page height fits the viewport and only `.messages` scrolls; buttons «Чаты» / «Источники» open left/right drawers; `test_history_and_sources_reachable_on_narrow_window` green.

## Out of scope

- Merging `features/chat` into `dev` (human decides push order).
- Starting story 7 (Викторины).
