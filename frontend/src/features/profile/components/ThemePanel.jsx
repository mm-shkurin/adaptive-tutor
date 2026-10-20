import { useTheme } from '../../../shared/theme/useTheme'

const CHOICES = [
  ['system', 'Системная'],
  ['light', 'Светлая'],
  ['dark', 'Темная'],
]

export function ThemePanel() {
  const { choice, setTheme } = useTheme()
  return (
    <section className="panel">
      <h3>Внешний вид</h3>
      <p className="meta">Оформление на этом устройстве</p>
      <div className="theme">
        {CHOICES.map(([value, label]) => (
          <button
            key={value}
            type="button"
            className={choice === value ? 'on' : undefined}
            data-testid={`theme-${value}`}
            aria-pressed={choice === value}
            onClick={() => setTheme(value)}
          >
            {label}
          </button>
        ))}
      </div>
    </section>
  )
}
