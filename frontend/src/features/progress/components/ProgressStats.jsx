export function ProgressStats({ stats }) {
  return (
    <div className="prog-stats" data-testid="prog-stats">
      {stats.map((stat) => (
        <div key={stat.key} className="prog-stat">
          <div className="prog-stat-val" data-testid={stat.testId}>
            {stat.value}
          </div>
          <div className="prog-stat-label">{stat.label}</div>
        </div>
      ))}
    </div>
  )
}