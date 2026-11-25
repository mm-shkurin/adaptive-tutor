from dataclasses import dataclass
from datetime import date, datetime, timedelta
from uuid import UUID

from domain.quiz.attempt import Score


def mastery_percent(score: Score) -> int:
    if score.total == 0:
        return 0
    return round(score.correct * 100 / score.total)


def mastery_band(mastery: int) -> str:
    if mastery >= 70:
        return "mastered"
    if mastery >= 40:
        return "medium"
    return "weak"


@dataclass(frozen=True)
class TopicFinish:
    material_id: UUID
    material_name: str
    topic: str
    mastery: int
    finished_at: datetime | None


def topic_key(material_id: UUID, topic: str) -> str:
    return f"{material_id}:{topic}"


def pick_latest_topics(rows: tuple[TopicFinish, ...]) -> tuple[TopicFinish, ...]:
    best: dict[tuple[UUID, str], TopicFinish] = {}
    for row in rows:
        key = (row.material_id, row.topic)
        prior = best.get(key)
        if prior is None or _is_newer(row, prior):
            best[key] = row
    return tuple(best.values())


def _is_newer(left: TopicFinish, right: TopicFinish) -> bool:
    if left.finished_at is None:
        return False
    if right.finished_at is None:
        return True
    return left.finished_at > right.finished_at


def average_mastery(topics: tuple[TopicFinish, ...]) -> int:
    if not topics:
        return 0
    return round(sum(topic.mastery for topic in topics) / len(topics))


def weak_topics(topics: tuple[TopicFinish, ...]) -> tuple[TopicFinish, ...]:
    return tuple(topic for topic in topics if topic.mastery < 40)


def local_day(moment: datetime) -> date:
    return moment.astimezone().date()


def sessions_this_week(moments: tuple[datetime, ...], now: datetime) -> int:
    end = local_day(now)
    start = end - timedelta(days=6)
    days = {local_day(moment) for moment in moments if start <= local_day(moment) <= end}
    return len(days)


def material_chip(document) -> dict:
    return {"id": str(document.id), "name": document.name, "kind": document.kind}


def topic_node(topic: TopicFinish) -> dict:
    return {
        "id": topic_key(topic.material_id, topic.topic),
        "name": topic.topic,
        "mastery": topic.mastery,
        "material_id": str(topic.material_id),
        "band": mastery_band(topic.mastery),
    }