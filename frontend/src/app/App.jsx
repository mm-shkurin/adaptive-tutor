import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { DeletedPage } from '../features/auth/DeletedPage'
import { OAuthCallbackPage } from '../features/auth/OAuthCallbackPage'
import { ChatPage } from '../features/chat/ChatPage'
import { DocumentsPage } from '../features/documents/DocumentsPage'
import { LandingPage } from '../features/landing/LandingPage'
import { ProfilePage } from '../features/profile/ProfilePage'
import { QuizzesPage } from '../features/quizzes/QuizzesPage'
import { AppShell } from '../features/shell/AppShell'
import { ProgressPage } from '../features/progress/ProgressPage'
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
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/quizzes/*" element={<QuizzesPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
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
