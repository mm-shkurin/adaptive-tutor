import { ProgressPanel } from './components/ProgressPanel'
import { useProgressScreen } from './useProgressScreen'

export function ProgressPage() {
  const screen = useProgressScreen()
  if (screen.status === 'loading') {
    return (
      <main className="progress-page" data-testid="progress-loading">
        <div className="spinner" aria-hidden="true" />
      </main>
    )
  }
  if (screen.status === 'error') {
    return (
      <main className="progress-page">
        <p className="alert" role="alert" data-testid="progress-error">
          Не удалось открыть прогресс.
        </p>
        <button type="button" className="btn btn-primary" data-testid="progress-retry" onClick={screen.retry}>
          Повторить
        </button>
      </main>
    )
  }
  return (
    <main className="progress-page" data-testid="progress">
      <div className="panel-head">
        <div>
          <h1>Ваш прогресс</h1>
          <p className="progress-lead">
            Ответы из чата и викторин собраны в карту тем по вашим материалам
          </p>
        </div>
      </div>
      <ProgressPanel screen={screen} />
    </main>
  )
}