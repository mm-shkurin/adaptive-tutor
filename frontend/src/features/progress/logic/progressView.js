export function formatMasteryPercent(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '0%'
  return `${Math.round(value)}%`
}

export function bandDotClass(band) {
  if (band === 'mastered') return 'prog-band-mastered'
  if (band === 'medium') return 'prog-band-medium'
  return 'prog-band-weak'
}

const WEAK_MASTERY_BELOW = 40

function topicRow(topic) {
  return {
    id: topic.id,
    name: topic.name,
    mastery: topic.mastery,
    masteryLabel: formatMasteryPercent(topic.mastery),
    materialId: topic.material_id,
    band: topic.band,
    bandClass: bandDotClass(topic.band),
  }
}

export function materialChips(materials, selectedMaterialId) {
  const chips = [{ id: null, label: 'Все материалы', active: selectedMaterialId == null }]
  for (const item of materials) {
    chips.push({ id: item.id, label: item.name, active: item.id === selectedMaterialId })
  }
  return chips
}

export function weakTopicsOnly(topics) {
  return topics.filter((topic) => topic.mastery < WEAK_MASTERY_BELOW)
}

export function progressView(body, selectedMaterialId = null) {
  const weakTopics = weakTopicsOnly(body.weak_topics.map(topicRow)).map((topic) => ({
    ...topic,
    barWidth: `${Math.round(topic.mastery)}%`,
  }))
  return {
    stats: [
      {
        key: 'mastery',
        testId: 'prog-mastery',
        value: formatMasteryPercent(body.average_mastery),
        label: 'Среднее усвоение',
      },
      {
        key: 'weak',
        testId: 'prog-weak-n',
        value: String(weakTopics.length),
        label: 'Слабые темы',
      },
      {
        key: 'sessions',
        testId: 'prog-sessions',
        value: String(body.sessions_this_week),
        label: 'Сессий за неделю',
      },
      {
        key: 'quizzes',
        testId: 'prog-quizzes',
        value: String(body.quizzes_finished),
        label: 'Викторины пройдены',
      },
    ],
    topicNodes: body.topics.map(topicRow),
    weakTopics,
    activity: (body.activity ?? []).map((item) => ({
      id: `${item.kind}-${item.at}-${item.title}`,
      title: item.title,
      kind: item.kind,
      at: item.at,
      meta: formatActivityWhen(item.at),
      warn: item.kind === 'quiz',
    })),
    materialChips: materialChips(body.materials, selectedMaterialId),
  }
}

function formatActivityWhen(iso) {
  if (typeof iso !== 'string' || !iso) return ''
  const stamp = Date.parse(iso)
  if (Number.isNaN(stamp)) return iso
  return new Date(stamp).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}