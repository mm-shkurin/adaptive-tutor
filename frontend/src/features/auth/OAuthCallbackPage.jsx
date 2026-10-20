import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { isSignedIn } from '../../shared/session/authSession'
import { exchangeOnce } from './api/oauthApi'
import { FailureGate, WaitingGate } from './AuthGates'
import { EXCHANGE_REFUSED, MALFORMED_CALLBACK, callbackOutcome } from './logic/callbackOutcome'

export function OAuthCallbackPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const [failure, setFailure] = useState(null)

  useEffect(() => {
    const outcome = callbackOutcome(params)
    if (outcome.kind === 'refused') {
      setFailure(outcome.reason)
      return
    }
    if (outcome.kind === 'malformed') {
      setFailure(MALFORMED_CALLBACK)
      return
    }
    let active = true
    exchangeOnce(outcome.code)
      .then(() => {
        if (active) navigate('/profile', { replace: true })
      })
      .catch(() => {
        if (!active) return
        if (isSignedIn()) navigate('/profile', { replace: true })
        else setFailure(EXCHANGE_REFUSED)
      })
    return () => {
      active = false
    }
  }, [params, navigate])

  if (failure) return <FailureGate reason={failure} onRetry={() => navigate('/', { replace: true })} />
  return <WaitingGate />
}
