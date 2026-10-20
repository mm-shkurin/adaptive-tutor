import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { beginSignIn, resetSignIn } from '../../shared/session/signIn'
import { useSession } from '../../shared/session/useSession'
import { WaitingGate } from '../auth/AuthGates'
import { Hero } from './components/Hero'
import { LandingBody } from './components/LandingBody'
import { LandingNav } from './components/LandingNav'

export function LandingPage() {
  const session = useSession()
  const [starting, setStarting] = useState(false)

  useEffect(() => {
    resetSignIn()
  }, [])

  useEffect(() => {
    if (starting) beginSignIn()
  }, [starting])

  if (session) return <Navigate to="/profile" replace />
  if (starting) return <WaitingGate />

  const start = () => setStarting(true)

  return (
    <div className="landing-shell" id="top" data-testid="landing">
      <div className="landing-top">
        <LandingNav onSignIn={start} />
        <Hero onSignIn={start} />
      </div>
      <LandingBody onSignIn={start} />
    </div>
  )
}
