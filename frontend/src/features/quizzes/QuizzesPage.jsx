import { QuizScreen } from './components/QuizScreen'
import { useQuizzesScreen } from './useQuizzesScreen'

export function QuizzesPage() {
  const screen = useQuizzesScreen()
  if (screen.status === 'loading' || screen.view === 'opening') {
    return (
      <main className="quizzes-page" data-testid="quiz-loading">
        <div className="spinner" aria-hidden="true" />
      </main>
    )
  }
  if (screen.status === 'error') {
    return (
      <main className="quizzes-page">
        <p className="alert" role="alert" data-testid="quiz-error">
          Не удалось открыть викторины.
        </p>
        <button type="button" className="btn btn-primary" data-testid="quiz-retry" onClick={screen.retry}>
          Повторить
        </button>
      </main>
    )
  }
  return <QuizScreen screen={screen} />
}
