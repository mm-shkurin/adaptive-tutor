export function QuizBack({ onClick, disabled = false, testId = 'quiz-back', label = '← К викторинам' }) {
  return (
    <button
      type="button"
      className="quiz-back"
      data-testid={testId}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  )
}
