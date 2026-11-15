## discussion (2026-11-15)

**Mistake:** Consolidation merged the empty-library screen with "a not-ready document cannot be chosen", and merged a document switch with the late reply.
**Why wrong:** Each merge narrowed the Given, so a library that still has a ready PDF, and a switch with no reply in flight, stopped being checked.
**Correct location/approach:** Those pairs stay separate: UI 0.2 and 0.3, API 7.1 and 7.2.
