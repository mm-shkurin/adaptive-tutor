from uuid import uuid4

from tests.presentation_flow import PROGRESS_MISSING
from tests.quiz_flow import ada, advance, answer, neighbour, post_quiz, ready_pdf, valid_body
from tests.test_presentation_chat import open_chat, send_question
from tests.support import bearer, build


def read(bundle, token, material=None):
    params = {} if material is None else {"material": str(material)}
    return bundle.client.get("/api/v1/progress", headers=bearer(token), params=params)


def send_chat(bundle, token, chat_id, text):
    bundle.tutor.script("По материалу.")
    return bundle.client.post(
        f"/api/v1/chats/{chat_id}/messages",
        headers={**bearer(token), "Idempotency-Key": str(uuid4())},
        json={"text": text, "mode": "professor", "model": "auto"},
    )


def finish_named(bundle, token, document_id, topic, count, correct):
    bundle.quiz_tutor.script(valid_body(count))
    quiz_id = post_quiz(bundle, token, document_id, count, topic=topic).json()["id"]
    from tests.quiz_flow import read as read_quiz

    detail = read_quiz(bundle, token, quiz_id).json()
    answered = 0
    while detail["status"] == "take":
        pick = 0 if answered < correct else 1
        chosen = detail["questions"][detail["current_index"]]["choices"][pick]["id"]
        answer(bundle, token, quiz_id, chosen)
        detail = advance(bundle, token, quiz_id).json()
        answered += 1
    assert detail["status"] == "result"
    return detail


def test_progress_foreign_material_filter():
    bundle = build()
    token, _ = ada(bundle)
    _, neighbour_owner = neighbour(bundle)
    foreign = ready_pdf(bundle, neighbour_owner, "secret.pdf")
    response = read(bundle, token, foreign.id)
    assert response.status_code == 404
    assert response.json() == PROGRESS_MISSING


def test_progress_weak_topics_and_count():
    bundle = build()
    token, owner = ada(bundle)
    low = ready_pdf(bundle, owner, "a.pdf")
    mid = ready_pdf(bundle, owner, "b.pdf")
    high = ready_pdf(bundle, owner, "c.pdf")
    finish_named(bundle, token, low.id, "weak topic", 8, 2)
    finish_named(bundle, token, mid.id, "mid topic", 8, 4)
    finish_named(bundle, token, high.id, "strong topic", 5, 4)
    body = read(bundle, token).json()
    assert body["weak_topic_count"] == 1
    assert len(body["weak_topics"]) == 1
    assert body["weak_topics"][0]["name"] == "weak topic"
    assert body["weak_topics"][0]["mastery"] == 25
    assert len(body["topics"]) == 3
    assert "edges" not in body


def test_progress_sessions_count_distinct_days():
    bundle = build()
    token, owner = ada(bundle)
    document = ready_pdf(bundle, owner, "study.pdf")
    bundle.clock.advance(-86400)
    chat_id = open_chat(bundle, token, str(document.id)).json()["id"]
    send_chat(bundle, token, chat_id, "yesterday")
    bundle.clock.advance(86400)
    finish_named(bundle, token, document.id, "today", 5, 5)
    send_chat(bundle, token, chat_id, "today one")
    send_chat(bundle, token, chat_id, "today two")
    body = read(bundle, token).json()
    assert body["sessions_this_week"] == 2