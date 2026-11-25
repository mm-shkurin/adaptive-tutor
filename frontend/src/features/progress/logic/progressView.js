export function formatMasteryPercent(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '0%'
  return `${Math.round(value)}%`
}

export function bandDotClass(band) {
  if (band === 'mastered') return 'prog-band-mastered'
  if (band === 'medium') return 'prog-band-medium'
  return 'prog-band-weak'
}

function topicRow(topic) {
  return {
    id: topic.id,
    name: topic.name,
    mastery: topic.mastery,
    masteryLabel: formatMasteryPercent(topic.mastery),
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

export function progressView(body, selectedMaterialId = null) {
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
        value: String(body.weak_topic_count),
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
    weakTopics: body.weak_topics.map((topic) => ({
      ...topicRow(topic),
      barWidth: `${Math.round(topic.mastery)}%`,
    })),
    materialChips: materialChips(body.materials, selectedMaterialId),
  }
}