export function MaterialFilter({ chips, onPick }) {
  if (chips.length <= 1) return null
  return (
    <div className="prog-filter" data-testid="prog-filter">
      {chips.map((chip) => (
        <button
          key={chip.id ?? 'all'}
          type="button"
          className={chip.active ? 'prog-chip active' : 'prog-chip'}
          data-testid={chip.id ? `prog-chip-${chip.id}` : 'prog-chip-all'}
          aria-pressed={chip.active}
          onClick={() => onPick(chip.id)}
        >
          {chip.label}
        </button>
      ))}
    </div>
  )
}