import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchProgress } from '../../shared/api/backend/progressApi'
import { isSessionExpired } from '../../shared/session/authorizedRequest'
import { endSession } from '../../shared/session/authSession'
import { progressView } from './logic/progressView'
import { chatForMaterialTarget, quizCreateTarget } from './logic/topicActions'

export function useProgressScreen() {
  const navigate = useNavigate()
  const [attempt, setAttempt] = useState(0)
  const [status, setStatus] = useState('loading')
  const [materialId, setMaterialId] = useState(null)
  const [selectedTopicId, setSelectedTopicId] = useState(null)
  const [panel, setPanel] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    setStatus('loading')
    fetchProgress(materialId, controller.signal)
      .then((body) => {
        if (controller.signal.aborted) return
        setPanel(progressView(body, materialId))
        setStatus('ready')
      })
      .catch((error) => {
        if (controller.signal.aborted) return
        if (leaveIfExpired(error, navigate)) return
        setStatus('error')
      })
    return () => controller.abort()
  }, [attempt, materialId, navigate])

  function pickMaterial(id) {
    setMaterialId(id)
    setSelectedTopicId(null)
  }

  function selectTopic(id) {
    setSelectedTopicId(id)
  }

  function startTopicQuiz(topic) {
    const target = quizCreateTarget(topic)
    if (target) navigate(target.path, { state: target.state })
  }

  function askTopicInChat(topic) {
    const target = chatForMaterialTarget(topic)
    if (target) navigate(target.path, { state: target.state })
  }

  return {
    status,
    panel,
    materialId,
    selectedTopicId,
    pickMaterial,
    selectTopic,
    startTopicQuiz,
    askTopicInChat,
    retry: () => setAttempt((value) => value + 1),
  }
}

function leaveIfExpired(error, navigate) {
  if (!isSessionExpired(error)) return false
  endSession()
  navigate('/', { replace: true })
  return true
}