# Spec-Skeptic Report

Loaded by `spec-skeptic`. The whole return is this document filled in. No prose
outside it.

## Verdict words

| Mode | Allowed `verdict` |
|------|-------------------|
| `sources` | `start` · `revise-sources` · `block` |
| `spec` | `accept` · `revise` · `block` |

`block` — a missing or contradictory source, or any HIGH that makes the spec
unacceptable as the basis for mockups and test-spec. `findings: []` only when
the pass genuinely found nothing.

## Ambiguity smells

Tag a sentence when two readers could write different tests from it:

1. Subjective modifiers with no threshold (`fast`, `appropriate`, `robust`, `should`).
2. Open lists and vague counts (`etc.`, `some`, `as needed`, `multiple`).
3. A pronoun whose noun is not unique.
4. A quantity with no unit, bound, or range.
5. Passive voice that hides who acts and when.
6. A term this story's sources never define.
7. `and`/`or` without a grouping.
8. An unresolved placeholder (`TBD`, `TODO`) left in a file about to be marked done.
9. A happy path with no stated behavior for the empty, refused, or repeated case.

High — a test cannot be written at all. Medium — a test needs an assumption.
Low — wording only.

## Return

```yaml
mode: sources | spec
verdict: start | revise-sources | accept | revise | block
findings:
  - severity: HIGH | MED | LOW
    where: <file:line | section | checklist item>
    problem: <what is missing, invented, or two-way>
    source: <which source says so, or "none">
    fix: <concrete edit or question>
coverage:                 # spec mode only
  - item: <source requirement>
    status: met | unmet | not_verified
    evidence: <section in the spec, or why it cannot be checked>
questions_to_user: []     # only ambiguities a source cannot resolve
```
