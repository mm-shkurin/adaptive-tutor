import { CreateQuizForm } from './CreateQuizForm'
import { QuizList } from './QuizList'
import { QuizResult } from './QuizResult'
import { QuizTake } from './QuizTake'

export function QuizScreen({ screen }) {
  if (screen.view === 'create') {
    return (
      <main className="quizzes-page" data-testid="quiz-page">
        <CreateQuizForm screen={screen} />
      </main>
    )
  }
  if (screen.view === 'take') {
    return (
      <main className="quizzes-page" data-testid="quiz-page">
        <QuizTake screen={screen} />
      </main>
    )
  }
  if (screen.view === 'result') {
    return (
      <main className="quizzes-page" data-testid="quiz-page">
        <QuizResult screen={screen} />
      </main>
    )
  }
  return (
    <main className="quizzes-page" data-testid="quiz-page">
      <QuizList screen={screen} />
    </main>
  )
}
