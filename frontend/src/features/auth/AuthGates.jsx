export function WaitingGate() {
  return (
    <main className="center">
      <section className="gate" data-testid="oauth-waiting">
        <h2>Входим через Яндекс</h2>
        <p className="lead">Ждём подтверждение. Сессия появится только после ответа.</p>
        <div className="spinner" aria-hidden="true" />
      </section>
    </main>
  )
}

export function FailureGate({ reason, onRetry }) {
  return (
    <main className="center">
      <section className="gate" data-testid="oauth-failure">
        <h2>Не удалось войти</h2>
        <p className="lead">{reason}</p>
        <button type="button" className="btn btn-primary" data-testid="oauth-retry" onClick={onRetry}>
          Вернуться на главную
        </button>
      </section>
    </main>
  )
}
