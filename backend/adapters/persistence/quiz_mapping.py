from datetime import datetime
from uuid import UUID

from adapters.persistence.quiz_tables import (
    QuizAnswerRow,
    QuizAttemptRow,
    QuizChoiceRow,
    QuizQuestionRow,
    QuizRow,
)
from domain.quiz.attempt import Answer, Attempt, Score
from domain.quiz.choice import Choice
from domain.quiz.question import Question
from domain.quiz.quiz import Quiz


def new_row(owner_id: UUID, quiz: Quiz, created_at: datetime, key: str) -> QuizRow:
    row = QuizRow(
        id=quiz.id,
        owner_id=owner_id,
        document_id=quiz.document_id,
        document_name=quiz.document_name,
        topic=quiz.topic,
        idempotency_key=key,
        created_at=created_at,
        last_correct=None,
        last_total=None,
        questions=[_question_row(quiz.id, index, question) for index, question in enumerate(quiz.questions)],
        answers=[],
    )
    apply_state(row, quiz)
    return row


def apply_state(row: QuizRow, quiz: Quiz, now: datetime | None = None) -> None:
    row.last_correct = None if quiz.last_score is None else quiz.last_score.correct
    row.last_total = None if quiz.last_score is None else quiz.last_score.total
    if quiz.last_score is not None and quiz.open_attempt is None and now is not None:
        row.finished_at = now
    _apply_attempt(row, quiz)
    _apply_answers(row, quiz)


def quiz_from_row(row: QuizRow) -> Quiz:
    attempt = None
    if row.attempt is not None:
        attempt = Attempt(row.attempt.current_index, _scoped(row, "open"))
    return Quiz(
        id=row.id,
        document_id=row.document_id,
        document_name=row.document_name,
        topic=row.topic,
        questions=tuple(_question(item) for item in row.questions),
        open_attempt=attempt,
        last_score=_score(row),
        done=_scoped(row, "done"),
    )


def _apply_attempt(row: QuizRow, quiz: Quiz) -> None:
    if quiz.open_attempt is None:
        row.attempt = None
        return
    if row.attempt is None:
        row.attempt = QuizAttemptRow(quiz_id=quiz.id, current_index=quiz.open_attempt.index)
        return
    row.attempt.current_index = quiz.open_attempt.index


def _apply_answers(row: QuizRow, quiz: Quiz) -> None:
    wanted = {_key(item): item for item in _answer_rows(quiz)}
    current = {_key(item): item for item in list(row.answers)}
    for key, answer in current.items():
        if key not in wanted:
            row.answers.remove(answer)
            continue
        answer.choice_id = wanted[key].choice_id
    for key, answer in wanted.items():
        if key not in current:
            row.answers.append(answer)


def _answer_rows(quiz: Quiz) -> tuple[QuizAnswerRow, ...]:
    open_answers = () if quiz.open_attempt is None else quiz.open_attempt.answers
    return _scope(quiz.id, "open", open_answers) + _scope(quiz.id, "done", quiz.done)


def _scope(quiz_id: UUID, scope: str, answers: tuple[Answer, ...]) -> tuple[QuizAnswerRow, ...]:
    return tuple(
        QuizAnswerRow(quiz_id=quiz_id, scope=scope, question_id=answer.question_id, choice_id=answer.choice_id)
        for answer in answers
    )


def _key(answer: QuizAnswerRow) -> tuple:
    return answer.scope, answer.question_id


def _question_row(quiz_id: UUID, position: int, question: Question) -> QuizQuestionRow:
    row = QuizQuestionRow(
        id=question.id,
        quiz_id=quiz_id,
        position=position,
        body=question.text,
        page=question.page,
        slide=question.slide,
        correct_choice_id=question.correct_choice_id,
    )
    row.choices = [
        QuizChoiceRow(id=choice.id, question_id=question.id, position=index, body=choice.text)
        for index, choice in enumerate(question.choices)
    ]
    return row


def _question(row: QuizQuestionRow) -> Question:
    return Question(
        row.id,
        row.body,
        tuple(Choice(item.id, item.body) for item in row.choices),
        row.correct_choice_id,
        row.page,
        row.slide,
    )


def _scoped(row: QuizRow, scope: str) -> tuple[Answer, ...]:
    return tuple(
        Answer(item.question_id, item.choice_id) for item in row.answers if item.scope == scope
    )


def _score(row: QuizRow) -> Score | None:
    if row.last_correct is None or row.last_total is None:
        return None
    return Score(row.last_correct, row.last_total)
