class ProgressNotFound(Exception):
    """No progress for this caller, or the caller is not signed in."""


class GetProgress:
    async def read(self, owner_id, material=None) -> dict:
        return {
            "average_mastery": 0,
            "weak_topic_count": 0,
            "sessions_this_week": 0,
            "quizzes_finished": 0,
            "topics": [],
            "weak_topics": [],
            "activity": [],
            "materials": [],
        }