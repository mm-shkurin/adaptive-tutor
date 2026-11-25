from datetime import datetime
from uuid import UUID

from domain.document.document import Document
from domain.presentation.progress_math import (
    TopicFinish,
    average_mastery,
    material_chip,
    mastery_percent,
    pick_latest_topics,
    sessions_this_week,
    topic_node,
    weak_topics,
)
from domain.quiz.quiz import Quiz


def build_progress(
    materials: tuple[Document, ...],
    finishes: tuple[tuple[Quiz, datetime], ...],
    person_sends: tuple[datetime, ...],
    material_filter: UUID | None,
    now: datetime,
) -> dict:
    scoped = _scope_finishes(finishes, material_filter)
    topic_rows = _topic_rows(scoped)
    topics = tuple(topic_node(topic) for topic in topic_rows)
    weak = tuple(topic_node(topic) for topic in weak_topics(topic_rows))
    moments = tuple(finished_at for _quiz, finished_at in scoped) + person_sends
    activity = _activity(scoped, person_sends)
    return {
        "average_mastery": average_mastery(topic_rows),
        "weak_topic_count": len(weak),
        "sessions_this_week": sessions_this_week(moments, now),
        "quizzes_finished": len(scoped),
        "topics": topics,
        "weak_topics": weak,
        "activity": activity,
        "materials": [material_chip(document) for document in materials],
    }


def _scope_finishes(
    finishes: tuple[tuple[Quiz, datetime], ...], material_filter: UUID | None
) -> tuple[tuple[Quiz, datetime], ...]:
    if material_filter is None:
        return finishes
    return tuple(row for row in finishes if row[0].document_id == material_filter)


def _topic_rows(finishes: tuple[tuple[Quiz, datetime], ...]) -> tuple[TopicFinish, ...]:
    rows = tuple(
        TopicFinish(
            quiz.document_id,
            quiz.document_name,
            quiz.topic,
            mastery_percent(quiz.last_score),
            finished_at,
        )
        for quiz, finished_at in finishes
        if quiz.last_score is not None
    )
    return pick_latest_topics(rows)


def _activity(
    finishes: tuple[tuple[Quiz, datetime], ...], person_sends: tuple[datetime, ...]
) -> list[dict]:
    items = [
        {
            "at": finished_at.isoformat().replace("+00:00", "Z"),
            "kind": "quiz",
            "title": f"Викторина: {quiz.topic}",
        }
        for quiz, finished_at in finishes
    ]
    items.extend(
        {
            "at": sent.isoformat().replace("+00:00", "Z"),
            "kind": "chat",
            "title": "Сообщение в чате",
        }
        for sent in person_sends
    )
    items.sort(key=lambda item: item["at"], reverse=True)
    return items[:50]