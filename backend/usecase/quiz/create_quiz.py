from uuid import UUID

from domain.chat.source import Source
from domain.quiz.errors import EmptyRetrieval
from domain.quiz.question import Question
from domain.quiz.quiz import Quiz
from domain.quiz.topic import Topic, require_count
from usecase.document.ports import DocumentIntake
from usecase.quiz.errors import DuplicateQuizKey, QuizNotFound
from usecase.quiz.ports import MaterialSearch, QuizStore, QuizTutor


class CreateQuiz:
    def __init__(self, documents: DocumentIntake, search: MaterialSearch, tutor: QuizTutor, quizzes: QuizStore, clock):
        self.documents = documents
        self.search = search
        self.tutor = tutor
        self.quizzes = quizzes
        self.clock = clock

    async def create(self, owner_id: UUID, document_id: UUID, topic, count, key: str):
        return await self.quizzes.with_key(
            owner_id, key, lambda: self._new(owner_id, document_id, topic, count, key)
        )

    async def _new(self, owner_id, document_id, topic_raw, count_raw, key: str):
        topic = Topic.parse(topic_raw)
        asked = require_count(count_raw)
        document = await self._document(owner_id, document_id)
        pieces = Source.cite(await self.search.matching(document.id, topic.text))
        if not pieces:
            raise EmptyRetrieval()
        payload = await self.tutor.compose("auto", topic.text, asked, pieces)
        quiz = Quiz.start(document, topic, Question.assemble(asked, pieces, payload))
        try:
            await self.quizzes.add(owner_id, quiz, self.clock.now(), key)
        except DuplicateQuizKey:
            return await self._replay(owner_id, key)
        return quiz

    async def _document(self, owner_id, document_id):
        found = await self.documents.get(owner_id, document_id)
        if found is None:
            raise QuizNotFound()
        Quiz.require_ready(found)
        return found

    async def _replay(self, owner_id, key):
        found = await self.quizzes.find_by_key(owner_id, key)
        if found is None:
            raise DuplicateQuizKey()
        return found
