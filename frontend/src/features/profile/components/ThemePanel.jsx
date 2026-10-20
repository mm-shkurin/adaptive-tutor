import { useTheme } from '../../../shared/theme/useTheme'

const CHOICES = [
  ['system', 'Системная'],
  ['light', 'Светлая'],
  ['dark', 'Темная'],
]

export function ThemePanel() {
  const { choice, setTheme } = useTheme()
  return (
    <section className="profile-card">
      <h2 className="profile-card-title">Внешний вид</h2>
      <p className="profile-card-sub">Оформление интерфейса на этом устройстве</p>
      <div className="profile-row">
        <div className="profile-row-label">Тема оформления</div>
        <div className="theme-switch" role="group" aria-label="Тема оформления">
          {CHOICES.map(([value, label]) => (
            <button
              key={value}
              type="button"
              className={choice === value ? 'theme-opt active' : 'theme-opt'}
              data-testid={`theme-${value}`}
              aria-pressed={choice === value}
              onClick={() => setTheme(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
    </section>
  )
}
