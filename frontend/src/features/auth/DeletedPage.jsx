import { useNavigate } from 'react-router-dom'

export function DeletedPage() {
  const navigate = useNavigate()
  return (
    <main className="center">
      <section className="gate" data-testid="account-deleted">
        <h2>Аккаунт удалён</h2>
        <p className="lead">Этот аккаунт стёрт. Вход через Яндекс создаст новый.</p>
        <button type="button" className="btn btn-primary" onClick={() => navigate('/')}>
          На главную
        </button>
      </section>
    </main>
  )
}
