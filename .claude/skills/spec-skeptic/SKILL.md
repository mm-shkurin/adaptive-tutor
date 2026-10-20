---
name: spec-skeptic
description: Fresh-context skeptic for a story spec. Mode sources attacks the interview and its sources before the spec is written (missing decisions, contradictions, invented scope, ambiguity). Mode spec checks the written spec against those sources before the story step is marked done. Use on /spec-skeptic, before writing a story spec, before marking the story spec done, or when the user asks to check a spec, run the skeptic, or find what the spec dropped.
---

# /spec-skeptic

ORCHESTRATOR. One skeptic subagent with fresh context — it did not draft the
spec, so it does not share the drafter's blind spots. The hazard-catalogue scan
is a separate pass; this one does not repeat it.

## Invocation

```
/spec-skeptic <story>              # mode auto: no story spec file yet → sources, else spec
/spec-skeptic <story> sources
/spec-skeptic <story> spec
```

`<story>` is a number or a folder under `ProductSpecification/stories/`.

## Steps

1. **Resolve** the folder and the mode. `sources` needs an interview file.
   Missing → stop and say so. `spec` needs the story file and its notes file.
2. **Spawn 1 agent** (`spec-skeptic`, foreground). If that type is not in the
   agent list, use a general-purpose agent told to read
   `.claude/agents/spec-skeptic.md` and follow it exactly, without editing.
   Prompt:
   > Story folder: `<folder>`. Mode: `<mode>`.
   > Return only the report in `.claude/templates/spec/spec-skeptic-report.md`.
   Pass nothing else from this conversation except the previous findings on a
   re-run. The fresh view is the point.
3. **Report** to the user: verdict, HIGH findings first, then MED, then
   `questions_to_user`. LOW — count only unless asked. Do not argue a finding
   away in the report. A disagreement goes after the report, with a reason; the
   user decides.
4. **Route:**
   - `start` / `accept` → sources: the spec may be drafted; spec: the story
     step may be marked done. `accept` with any coverage item `not_verified`
     is invalid — treat it as `revise`.
   - `revise-sources` / `revise` → the user decides which findings to fold.
     Do not edit the spec inside this skill. After edits, re-run the same mode
     and pass the previous findings so each one is verified.
   - `block` → do not draft and do not mark the story step done. Show the
     blocking finding and ask the user.

Story-spec generation calls this same agent after the hazard scan, as its own
phase. A `block` or an unresolved HIGH there leaves the story checkbox open.
