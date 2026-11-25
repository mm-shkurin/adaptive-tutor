# Decision — AFK defaults for interview gaps (story 3)

Date: 2026-11-25. Source: `interview.md` «Не закрыто» + AFK defaults in `AFK_ISSUES.md`.

**DECISION: delete presentation removes the material only.**
Vectors, pieces, slide bytes (if any remain), and the presentation row go away. Chats and quiz attempts that referenced the id are not cascade-deleted. Later open/create against that id is refused as absent. UI that still holds a stale title shows «Источник удалён» when the join fails.

**DECISION: knowledge graph ships nodes without edges.**
Topic nodes use the decided color bands. Edges are out of this story until a rule names them.

**DECISION: weak counter and weak list use &lt;40% only.**
Medium topics stay on the graph; they are not counted as weak.

**DECISION: weekly sessions are distinct active days.**
A day counts once if the owner sent ≥1 chat message or finished ≥1 quiz attempt that day, within the last seven local midnights.

**DECISION: photo / PPTX / DOCX use the same virus check as PDF.**
Failure, timeout, or unreadable virus reply refuses that add and stores no bytes for it.

**DECISION: story 8 Progress is delivered inside story 3.**
The separate backlog row for story 8 is retired from the delivery queue.
