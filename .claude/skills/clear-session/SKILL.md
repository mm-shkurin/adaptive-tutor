---
name: clear-session
description: >-
  Persist journey context via /handoff, push the current branch to origin, report
  what was saved, then instruct the user to clear the chat and resume with
  /continue. Use when the user types /clear-session, /clear, asks to clear the
  chat after documenting progress, or wants a Claude-style save-then-reset before
  starting a fresh conversation.
---

# /clear-session — Save, push, then clear

End-of-session ritual: **document → push branch → clear**. The agent cannot close
the Cursor chat UI; this skill does the durable write, backs the branch up on the
remote, and tells the user the one action that resets context.

## Workflow

1. **Run `/handoff` fully** — follow `.claude/skills/handoff/SKILL.md` end-to-end
   (identify work item, review window, append or "nothing to record", promote
   carryover if a scenario completed). Do not invent a parallel summary format;
   `/handoff` is the sole writer of journey summaries and carryover.

2. **Progress snapshot (read-only)** — if a story/task `progress.md` is in play,
   state in one short line: work item name, last `[x]` / current `[~]` / next
   `[ ]`. Do not edit `progress.md` here (that belongs to `/continue`).

3. **Push the current branch to origin** — every `/clear-session` backs the
   session up on the remote before the user clears the chat:

   ```bash
   git push -u origin HEAD
   ```

   - Push the **working branch** (`features/…`, `feat/…`, …), not
     `git push origin <branch>:main`. Landing on `main` stays a separate,
     explicit step (see `.claude/rules/git.md` / delivery-loop).
   - Do not invent a commit here. If the tree has uncommitted work, push what is
     already committed and mention the dirty paths in the closing block.
   - If there is no remote, push is rejected, or HEAD has nothing new, say so in
     the closing block — still proceed to the clear instructions.
   - Never force-push unless the user explicitly asked for it in this turn.

4. **Agent log note (optional)** — if this conversation dispatched sub-agents,
   remind that live milestones live in `infrastructure/agent-progress.log`. Do
   not wipe that file unless the user explicitly asked to clear the log.

5. **Stop and hand the clear to the user** — after handoff + push, output exactly
   this closing block (fill the bracketed bits):

```
Saved. Safe to clear.

• Handoff: {files touched / "nothing to record"}
• Progress: {one-line snapshot or "no active progress.md"}
• Push: {branch → origin / "nothing to push" / "failed: …"}
• Clear chat:
  - Agent UI → New Chat
  - Cursor CLI → /clear  (aliases: /new, /new-chat)
• Resume: in the new chat type /continue
```

6. **Do not continue working** after the closing block. No more tool calls for
   implementation. Wait for the user in a fresh chat.

## Constraints

- Never claim the chat was cleared — only the user (or CLI `/clear`) does that.
- Never skip `/handoff` or the origin push to "save time"; an empty
  "nothing to record" is fine, and a no-op / failed push must still be reported.
- Do not run `/continue` inside this skill; that is the next session.
- Do not `/compact` or summarize as a substitute for handoff files on disk.
- Do not merge into `main` as part of `/clear-session`.

## Authoritative References

- `.claude/skills/handoff/SKILL.md`
- `.claude/skills/continue/SKILL.md`
- `.claude/templates/workflow/summary-format.md`
- `.claude/rules/git.md`
