import asyncio
from uuid import UUID, uuid4

from dataclasses import replace

from domain.chat.source import Source
from domain.document.document import Document
from tests.support import auth_profile, bearer, build, sign_in


def valid_body(count: int, page: int = 2) -> dict:
    return {
        "questions": [
            {
                "text": f"Question {index}",
                "choices": [f"q{index}c{choice}" for choice in range(4)],
                "correct_index": 0,
                "page": page,
            }
            for index in range(count)
        ]
    }


def ada(bundle):
    token = sign_in(bundle).json()["access_token"]
    return token, UUID(auth_profile(bundle, token).json()["id"])


def neighbour(bundle):
    token = sign_in(bundle, "grace", "ya-grace", "grace@yandex.ru", "Grace").json()["access_token"]
    return token, UUID(auth_profile(bundle, token).json()["id"])


def ready_pdf(bundle, owner, name, seed=True):
    document = Document.accepted(name, 128).ready(3, 2)
    asyncio.run(bundle.intake.store(owner, document, b"%PDF-1.4", str(uuid4())))
    if seed:
        bundle.search.seed(document.id, (Source(page=2, text="alpha"), Source(page=4, text="beta")))
    return document


def unready_pdf(bundle, owner, name, state):
    document = Document.accepted(name, 128)
    if state == "indexing":
        document = document.indexing()
    elif state == "failed":
        document = document.indexing().failed("forced")
    asyncio.run(bundle.intake.store(owner, document, b"%PDF-1.4", str(uuid4())))
    if state == "a status that is not a known document status":
        document = replace(document, status="corrupted")
        asyncio.run(bundle.intake.save(document))
    return document


def post_quiz(bundle, token, document_id, count=None, topic="cells", key=None):
    stored = 5 if count is None else count
    bundle.quiz_tutor.script(valid_body(stored))
    body = {"document_id": str(document_id), "topic": topic}
    if count is not None:
        body["question_count"] = count
    return bundle.client.post(
        "/api/v1/quizzes",
        headers={**bearer(token), "Idempotency-Key": key or str(uuid4())},
        json=body,
    )


def answer(bundle, token, quiz_id, choice_id):
    return bundle.client.post(
        f"/api/v1/quizzes/{quiz_id}/answers",
        headers=bearer(token),
        json={"choice_id": choice_id},
    )


def advance(bundle, token, quiz_id):
    return bundle.client.post(f"/api/v1/quizzes/{quiz_id}/advance", headers=bearer(token))


def retry(bundle, token, quiz_id):
    return bundle.client.post(f"/api/v1/quizzes/{quiz_id}/retries", headers=bearer(token))


def read(bundle, token, quiz_id):
    return bundle.client.get(f"/api/v1/quizzes/{quiz_id}", headers=bearer(token))


def listed(bundle, token):
    return bundle.client.get("/api/v1/quizzes", headers=bearer(token))


def hidden(question) -> None:
    assert question["page"] is None
    assert question["correct_choice_id"] is None
    assert question["correct"] is None
    assert question["chosen_choice_id"] is None


def finish(bundle, token, quiz_id, how):
    detail = read(bundle, token, quiz_id).json()
    while detail["status"] == "take":
        pick = 0 if how == "right" else 1
        chosen = detail["questions"][detail["current_index"]]["choices"][pick]["id"]
        assert answer(bundle, token, quiz_id, chosen).status_code == 200
        advanced = advance(bundle, token, quiz_id)
        assert advanced.status_code == 200
        detail = advanced.json()
    return detail
