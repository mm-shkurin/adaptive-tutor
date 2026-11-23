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

## RCA

Checked against `features/chat` @ `5955ae6` (committed chat, before the uncommitted draft). The draft is the proposed fix, not the defect.

### Symptom (authoritative source)

- **Observable (language):** a Russian question can come back as an English tutor line. No assertion in the suite checks reply language. The only language check in the working tree is `backend/tests/test_http_tutor.py::test_five_year_old_uses_the_plain_words_system_prompt`, which asserts the substring `"same language"` inside the **system** message of the outgoing HTTP body — not the assistant text.
- **Source:** Task 3 spec, “live poke” on Vite `:5174` + API `:8010` with `FREE_LLM_CHAT_URL`. This session did not replay that poke against a model.
- **Frequency:** spec says intermittent per model. No pass/fail count was recorded.
- **Observable (layout):** at `max-width: 960px`, committed `frontend/src/styles/chat.css` sets `.chat-layout { height: auto }` and `.chat-side, .source-side { max-height: 180px }`. `.chat-page` is only `min-height: calc(100vh - 120px)` — no `max-height`, no `overflow`. Committed `ChatScreen.jsx` always renders `ChatList` and `SourcesPanel` in document flow; there is no drawer toggle and no `is-open`.
- **Source:** `git show HEAD` of those two files. Computed `scrollHeight` vs viewport was not measured in a browser this session.
- **Frequency:** every viewport ≤960px (CSS media query), not intermittent.

### Assumptions audit

| Prior claim | Status | Evidence |
|-------------|--------|----------|
| `_MODE_SYSTEM` and user content lack a same-language rule | verified | `git show HEAD:backend/adapters/tutor/http_tutor.py`: four system strings are English instructions with no “language”/“Russian”; `_user_content` returns only `Material:` + `Question:`. |
| Narrow `.chat-layout` / `.chat-page` grow the document | verified (rules) | HEAD `.chat-page` has min-height only. At ≤960px `.chat-layout` is `height: auto` while `.messages` is `overflow-y: auto` inside a grid row that sizes to content. Pixel scroll was not measured. |
| Chat list stays in flow on narrow | verified | HEAD `ChatScreen.jsx` always mounts `ChatList` inside `.chat-layout`. HEAD CSS caps `.chat-side` at `max-height: 180px` and does not take it out of flow. Spec’s “~140px” was not remeasured; the rule is 180px. |
| Live tutor is `HttpTutor` and the question is not rewritten | verified | `application/context.py` wires `SendMessage(..., HttpTutor(settings.free_llm_chat_url, ...))`. `SendMessage._answer` passes `question` through to `tutor.answer`. |
| Frontend translates the question to English | refuted | No chat client rewrite of the outgoing question text. The prompt language is chosen in `HttpTutor`. |

### Hypotheses

| # | Candidate cause | Evidence gathered | Label | Verdict |
|---|-----------------|-------------------|-------|---------|
| 1 | English-only system prompt and user wrapper give the model no same-language constraint, so a Russian question can be answered in English | HEAD prompt text has no language rule; question reaches `HttpTutor.answer` unchanged; assistant text is returned as the model wrote it (`_assistant_text`) | MEASURED (prompt + path). English reply itself not re-run | confirmed as the prompt mechanism |
| 2 | Another tutor adapter or a frontend translator rewrites the question into English | Only `HttpTutor` is wired for send; `ScriptedTutor` / `RefusingTutor` are not on that path; frontend has no translation step | MEASURED | refuted |
| 3 | `.messages` has no overflow, so the thread cannot scroll | HEAD `.messages` is `overflow-y: auto; min-height: 0`. The narrow rule sets the parent grid to `height: auto`, so the scrollport grows with the thread and the document scrolls | MEASURED (rules). REASONED (which box actually scrolls) | refuted as the missing-overflow story; confirmed as unbounded parent height |
| 4 | JS fails to lock `document` scroll | `ChatScreen` has no scroll handler. Layout is CSS-only | MEASURED | refuted |
| 5 | Chat list is a top strip because the narrow rule keeps `.chat-side` in the single-column grid | HEAD media query: one column, `height: auto`, side panels `max-height: 180px`, no `position: fixed` | MEASURED | confirmed |

### Conclusion

- **Root cause:** (1) `HttpTutor` builds an English system message and a user message with no same-language line, and returns the model text unchanged — a Russian question is not required to stay Russian. (2) Under 960px the chat grid is `height: auto` and the page has no viewport cap, so `.messages` grows with the thread and the document scrolls. (3) The same media query leaves `.chat-side` and `.source-side` in flow (`max-height: 180px`), and the screen never offers a drawer.
- **Measured:** HEAD prompt strings; `SendMessage` → `HttpTutor` call; HEAD CSS media query and page min-height; HEAD `ChatScreen` always-in-flow list.
- **Reasoned:** an English instruction stack is why replies drift to English; `height: auto` on the grid is why `.messages` does not become the scrollport. No live model call and no computed layout this session.
- **Residual unknowns:** how often the current model still answers English once the language line exists (model compliance, not the missing instruction). Exact document `scrollHeight` on an 800px window was not measured.
- **Fix lever:** add the same-language line on every mode’s system prompt and on the user wrapper; lock `.chat-page` to the viewport and move the list and sources off-canvas under 960px, opened by toggles. Designed next, not in this section.
