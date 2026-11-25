# Presentations from slides

Decisions below come from `interview.md` (2026-11-25) plus AFK defaults in `AFK_ISSUES.md` / `decisions/afk-defaults-decision.md`. The primary person is a signed-in student. The feature works when that student can build a presentation from photos, camera, own PDF pages, PPTX or DOCX, index it, use it in chat and quizzes with slide citations, delete it, and see progress fed by quizzes and examiner grades.

## Brief Description

A signed-in person builds a slide deck (gallery, camera, own PDF pages, PPTX, DOCX), indexes recognized text (OCR, LLM only when OCR is weak), uses the ready deck in chat and quizzes with «Слайд N» citations, and sees mastery progress for their materials.

## Prerequisites

- The person is signed in. A guest sees the landing, as in story 1.
- Ordinary PDF upload, virus check, TEI, Qdrant, chat, and quizzes already work (stories 2, 4, 7). This story does not reopen PDF ingestion rules for ordinary PDFs.
- A PDF page can be added as a slide only from a ready PDF owned by this person.

## Flow

1. On Documents, «Создать презентацию» opens the editor (empty draft, default title, 0 slides). Draft may be saved empty.
2. The person sets a title (≤80 chars), adds slides from gallery, camera (`capture=environment` in the browser — no separate camera API), selected pages of an owned ready PDF (append in selection order), or a whole PPTX/DOCX (local parse; embedded images take the photo path). Drag reorder changes slide order. At most 40 slides may be indexed.
3. «Готово · индексировать» with 1–40 slides runs virus check on new bytes, then OCR on each image slide; chat-LLM is called only when OCR text is thin for the image size or looks like a broken formula. Parser text/tables from PPTX/DOCX are kept without OCR. Bytes are erased after index. Empty recognition leaves the slide visible as empty and out of the search index; other slides can still make the deck ready.
4. Ready presentation appears in the materials list (`kind: presentation`) and can be bound to chat and chosen for quiz create. Citation: photo/PPTX/DOCX slide → «Слайд N»; PDF page inside a deck → «Слайд N, стр. M»; ordinary PDF chat/quiz stays page-only. Formula phrase and LaTeX are shown together when both exist; embeddings use the phrase.
5. Editing a ready deck edits recognized text (photos are gone). Status stays ready until a new index replaces vectors. While replacement runs, chat may still answer on old vectors. Draft is never ready for chat/quiz.
6. Deleting one presentation removes that material, pieces, and vectors. Chats and quiz attempts that pointed at it are not cascade-deleted; later use of that id is refused as absent.
7. Progress (`/progress`): filter by this person's materials; average mastery; weak-topic count and list (&lt;40% only); sessions this week (distinct active days, last 7 local midnights); finished quiz count; knowledge graph nodes (no edges); weak list; activity. Topic mastery = last finished quiz score for that topic on that material; an examiner grade moves that topic when its citation hits a question of that topic — otherwise activity only. «Викторина по теме» creates a quiz; «Спросить в чате» opens that material's chat.

## Acceptance Criteria

- Guest cannot create, edit, index, delete, or read presentations or progress.
- Empty draft saves; index with 0 or &gt;40 slides is refused; 1–40 indexes within the same 5-minute ceiling as PDF.
- Virus failure on photo/PPTX/DOCX refuses that add; PDF virus rules for ordinary upload stay unchanged.
- OCR/LLM are faked in automated tests; live OCR/model poke is out of the green pipeline.
- Ready presentation is usable in chat and quiz with slide citations; ordinary PDF citations stay page-only.
- Delete removes searchability of that deck and refuses later bind/create; other owners' materials stay.
- Progress weak counter matches &lt;40% topics; graph has nodes without edges; weekly sessions count distinct active days.

## Validation Rules

| Field | Rule |
|-------|------|
| Title | 1–80 characters after trim; empty after trim refused on index (draft may keep placeholder until then). |
| Slides to index | 1–40 inclusive. |
| Photo | jpeg, png, webp; each ≤ 50 MB; virus gate required. |
| PPTX / DOCX | ≤ 50 MB; virus gate; local parse. |
| PDF page source | Ready owned PDF only. |
| Session | Signed-in owner required. |
| Progress filter | This person's materials only. |

## Screen States

- Documents list with working «Создать презентацию» and presentation rows (draft / indexing / ready / failed).
- Editor: title, slide grid, add (gallery / camera / PDF pages / office), reorder, remove slide, save draft, index.
- Ready editor: recognized text per slide (no photos), reorder, re-index, delete.
- Progress: filter chips, four stats, graph nodes, weak list, activity, topic actions.

## Core Requirements

- Reuse TEI (`all-MiniLM-L6-v2`, 384), Qdrant, virus adapter, chat LLM URL, quiz create channel — do not invent parallel stacks.
- Embeddings use the readable formula phrase, never LaTeX alone.
- Story 8 is not a separate delivery; Progress is part of this story.
- Ordinary PDF path (story 2) and page-only citations for plain PDFs stay as they are.
