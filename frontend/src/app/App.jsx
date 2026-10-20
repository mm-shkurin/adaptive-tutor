import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { DeletedPage } from '../features/auth/DeletedPage'
import { OAuthCallbackPage } from '../features/auth/OAuthCallbackPage'
import { LandingPage } from '../features/landing/LandingPage'
import { ProfilePage } from '../features/profile/ProfilePage'
import { AppShell } from '../features/shell/AppShell'
import { SoonPage } from '../features/shell/SoonPage'
import { useSession } from '../shared/session/useSession'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/auth/callback" element={<OAuthCallbackPage />} />
      <Route path="/account-deleted" element={<DeletedPage />} />
      <Route element={<RequireSession />}>
        <Route element={<AppShell />}>
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/chat" element={<SoonPage title="Чат" />} />
          <Route path="/quizzes" element={<SoonPage title="Викторины" />} />
          <Route path="/progress" element={<SoonPage title="Прогресс" />} />
          <Route path="/documents" element={<SoonPage title="Документы" />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function RequireSession() {
  const session = useSession()
  if (!session) return <Navigate to="/" replace />
  return <Outlet />
}
