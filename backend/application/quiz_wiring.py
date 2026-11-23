from usecase.quiz.create_quiz import CreateQuiz
from usecase.quiz.play import AdvanceQuiz, AnswerQuiz, RetryQuiz
from usecase.quiz.read import GetQuiz, ListQuizzes


def wire_quizzes(documents, search, tutor, quizzes, clock) -> dict:
    return {
        "create_quiz": CreateQuiz(documents, search, tutor, quizzes, clock),
        "list_quizzes": ListQuizzes(quizzes),
        "get_quiz": GetQuiz(quizzes),
        "answer_quiz": AnswerQuiz(quizzes),
        "advance_quiz": AdvanceQuiz(quizzes),
        "retry_quiz": RetryQuiz(quizzes),
    }
