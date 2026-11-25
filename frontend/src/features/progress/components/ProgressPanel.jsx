import { ProgressStats } from './ProgressStats'
import { MaterialFilter } from './MaterialFilter'
import { TopicNodesCard } from './TopicNodesCard'
import { WeakTopicsCard } from './WeakTopicsCard'

export function ProgressPanel({ screen }) {
  const { panel } = screen
  if (!panel) return null
  return (
    <>
      <MaterialFilter chips={panel.materialChips} onPick={screen.pickMaterial} />
      <ProgressStats stats={panel.stats} />
      <div className="progress-grid">
        <TopicNodesCard nodes={panel.topicNodes} />
        <WeakTopicsCard topics={panel.weakTopics} />
      </div>
    </>
  )
}