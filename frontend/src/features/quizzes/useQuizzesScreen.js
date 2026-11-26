import { useEffect, useRef, useState } from 'react'
import { useLocation, useMatch, useNavigate } from 'react-router-dom'
import { failureText } from '../../shared/api/failureText'
import { httpErrorIn } from '../../shared/api/httpResponse'
import {
  advanceQuiz,
  answerQuiz,
  createQuiz,
  getQuiz,
  listQuizzes,
  retryQuiz,
} from '../../shared/api/backend/quizApi'
import { listDocuments } from '../../shared/api/backend/documentApi'
import { endSession } from '../../shared/session/authSession'
import { isSessionExpired } from '../../shared/session/authorizedRequest'
import {
  DEFAULT_QUESTION_COUNT,
  DOCUMENTS_UNAVAILABLE,
  createFailureMessage,
  createFormNotice,
  readyPdfChoices,
  validateCreate,
} from './logic/createQuiz'
import {
  cardRows,
  currentQuestion,
  missingQuizText,
  resultView,
  screenView,
  shouldAdvance,
  shouldSendChoice,
  takeView,
  withQuizCard,
} from './logic/quizView'

export function useQuizzesScreen() {
  const navigate = useNavigate()
  const location = useLocation()
  const isNew = Boolean(useMatch({ path: '/quizzes/new', end: true }))
  const playMatch = useMatch({ path: '/quizzes/:quizId', end: true })
  const quizId = isNew ? null : (playMatch?.params.quizId ?? null)
  const isNewRef = useRef(isNew)
  isNewRef.current = isNew
  const heldQuizId = useRef(null)
  const seed = location.state && typeof location.state === 'object' ? location.state : null

  const [attempt, setAttempt] = useState(0)
  const [status, setStatus] = useState('loading')
  const [quizzes, setQuizzes] = useState([])
  const [documents, setDocuments] = useState([])
  const [documentsFailed, setDocumentsFailed] = useState(false)
  const [quiz, setQuiz] = useState(null)
  const [topic, setTopic] = useState(() => (typeof seed?.topic === 'string' ? seed.topic : ''))
  const [questionCount, setQuestionCount] = useState(DEFAULT_QUESTION_COUNT)
  const [documentId, setDocumentId] = useState(() =>
    typeof seed?.documentId === 'string' ? seed.documentId : '',
  )
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState(null)
  const [listError, setListError] = useState(null)
  const [playError, setPlayError] = useState(null)
  const [busy, setBusy] = useState(false)
  const createLock = useRef(false)
  const actionLock = useRef(false)
  const wasPlaying = useRef(false)

  useEffect(() => {
    const controller = new AbortController()
    setStatus('loading')
    Promise.allSettled([
      listQuizzes(controller.signal),
      listDocuments(controller.signal),
    ]).then((results) => {
      if (controller.signal.aborted) return
      const [listed, docs] = results
      if (listed.status === 'rejected') {
        if (!leaveIfExpired(listed.reason, navigate)) setStatus('error')
        return
      }
      setQuizzes(listed.value.quizzes)
      if (docs.status === 'fulfilled') {
        setDocuments(docs.value.documents ?? [])
        setDocumentsFailed(false)
      } else if (leaveIfExpired(docs.reason, navigate)) {
        return
      } else {
        setDocuments([])
        setDocumentsFailed(true)
      }
      setStatus('ready')
    })
    return () => controller.abort()
  }, [attempt, navigate])

  useEffect(() => {
    if (!quizId) return undefined
    const controller = new AbortController()
    setQuiz((current) => (current?.id === quizId ? current : null))
    getQuiz(quizId, controller.signal)
      .then((detail) => {
        if (controller.signal.aborted) return
        heldQuizId.current = null
        setQuiz(detail)
      })
      .catch((error) => {
        if (controller.signal.aborted) return
        if (leaveIfExpired(error, navigate)) return
        if (heldQuizId.current === quizId) return
        const http = httpErrorIn(error)
        setListError(missingQuizText(http?.errorCode, http?.status) ?? failureText(error))
        navigate('/quizzes', { replace: true })
      })
    return () => controller.abort()
  }, [quizId, attempt, navigate])

  useEffect(() => {
    if (quizId) {
      wasPlaying.current = true
      return undefined
    }
    if (!wasPlaying.current) return undefined
    wasPlaying.current = false
    const controller = new AbortController()
    listQuizzes(controller.signal)
      .then((listed) => {
        if (!controller.signal.aborted) setQuizzes(listed.quizzes)
      })
      .catch((error) => {
        if (!controller.signal.aborted && leaveIfExpired(error, navigate)) return
      })
    return () => controller.abort()
  }, [quizId, navigate])

  const pdfs = readyPdfChoices(documents)
  const selectedDocumentId = pdfs.some((item) => item.id === documentId)
    ? documentId
    : (pdfs[0]?.id ?? '')
  const view = screenView({ isNew, quizId, quiz })

  function retry() {
    setAttempt((value) => value + 1)
  }

  function openCreate() {
    setTopic('')
    setQuestionCount(DEFAULT_QUESTION_COUNT)
    setCreateError(null)
    setListError(null)
    navigate('/quizzes/new')
  }

  function openQuiz(id) {
    setListError(null)
    setPlayError(null)
    navigate(`/quizzes/${id}`)
  }

  function backToList() {
    setCreateError(null)
    setPlayError(null)
    navigate('/quizzes')
  }

  async function generate(event) {
    event?.preventDefault?.()
    if (createLock.current) return
    if (documentsFailed) {
      setCreateError(DOCUMENTS_UNAVAILABLE)
      return
    }
    const ready = readyPdfChoices(documents)
    const selected = ready.some((item) => item.id === documentId) ? documentId : (ready[0]?.id ?? '')
    const check = validateCreate({
      documentId: selected,
      topic,
      questionCount,
      readyIds: ready.map((item) => item.id),
    })
    if (!check.ok) {
      setCreateError(check.message)
      return
    }
    createLock.current = true
    setCreating(true)
    setCreateError(null)
    const key = crypto.randomUUID()
    try {
      const created = await createQuiz(check.body, key)
      setQuizzes((rows) => withQuizCard(rows, created))
      if (!isNewRef.current) return
      heldQuizId.current = created.id
      setQuiz(created)
      navigate(`/quizzes/${created.id}`)
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setCreateError(createFailureMessage(error))
    } finally {
      createLock.current = false
      setCreating(false)
    }
  }

  async function choose(choiceId) {
    const question = currentQuestion(quiz)
    if (!shouldSendChoice(question)) return
    if (!lockAction()) return
    setPlayError(null)
    try {
      const next = await answerQuiz(quiz.id, choiceId)
      adopt(next)
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setPlayError(failureText(error))
    } finally {
      unlockAction()
    }
  }

  async function advance() {
    const question = currentQuestion(quiz)
    if (!shouldAdvance(question)) return
    if (!lockAction()) return
    setPlayError(null)
    try {
      const next = await advanceQuiz(quiz.id)
      adopt(next)
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setPlayError(failureText(error))
    } finally {
      unlockAction()
    }
  }

  async function playAgain() {
    if (quiz?.status !== 'result') return
    if (!lockAction()) return
    setPlayError(null)
    try {
      const next = await retryQuiz(quiz.id)
      adopt(next)
    } catch (error) {
      if (leaveIfExpired(error, navigate)) return
      setPlayError(failureText(error))
    } finally {
      unlockAction()
    }
  }

  function adopt(next) {
    setQuiz((current) => (current?.id === next.id ? next : current))
    setQuizzes((rows) => withQuizCard(rows, next))
  }

  function lockAction() {
    if (actionLock.current) return false
    actionLock.current = true
    setBusy(true)
    return true
  }

  function unlockAction() {
    actionLock.current = false
    setBusy(false)
  }

  return {
    status,
    retry,
    view,
    cards: cardRows(quizzes),
    pdfs,
    formNotice: createFormNotice({ documentsFailed, pdfCount: pdfs.length }),
    documentsFailed,
    listError,
    selectedDocumentId,
    setDocumentId,
    topic,
    setTopic,
    questionCount,
    setQuestionCount,
    creating,
    createError,
    playError,
    busy,
    take: view === 'take' ? takeView(quiz) : null,
    result: view === 'result' ? resultView(quiz) : null,
    openCreate,
    openQuiz,
    backToList,
    generate,
    choose,
    advance,
    playAgain,
  }
}

function leaveIfExpired(error, navigate) {
  if (!isSessionExpired(error)) return false
  endSession()
  navigate('/', { replace: true })
  return true
}
