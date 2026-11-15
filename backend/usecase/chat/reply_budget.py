from datetime import datetime, timedelta

CHAT_LATENCY = timedelta(seconds=5)


def deadline_at(started: datetime, latency: timedelta = CHAT_LATENCY) -> datetime:
    return started + latency


def remaining_seconds(started: datetime, now: datetime, latency: timedelta = CHAT_LATENCY) -> float:
    return (deadline_at(started, latency) - now).total_seconds()


def expired(started: datetime, now: datetime, latency: timedelta = CHAT_LATENCY) -> bool:
    return now >= deadline_at(started, latency)
