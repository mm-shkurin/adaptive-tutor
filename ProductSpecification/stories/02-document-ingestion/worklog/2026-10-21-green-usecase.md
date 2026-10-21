# green-usecase — 2026-10-21

Scenario: 4.1 An accepted PDF becomes ready and its text and tables can be searched
Docker was not used.

## Result

An accepted PDF is stored as waiting and returned before indexing. The worker then claims that waiting document, keeps its text and table as pieces, marks it ready, and deletes that document's file. A neighbour who already finished indexing has no file left; their pieces stay.

The scenario check changed with that rule: the neighbour file is already gone. The acceptance test stays skipped.

## Coverage

`pytest usecase/tests --cov=domain/document --cov=usecase/document --cov-branch`: 1 passed, 0 failed.

Focused gaps:
- `extracted_text.py` 23→25, reachable. Steps added: exact 500 tokens leaves no remainder.
- `index_documents.py` 16, no waiting document. Left to scenario 4.7.
- `read_document.py` 14 and `search_documents.py` 13, 18, missing document. Left to security 3.1.

## Tests

`pytest tests usecase/tests` from `backend/`: 46 passed, 0 failed, 0 skipped.
