import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { App } from './app/App'
import { initTheme } from './shared/theme/themeStore'
import './styles/tokens.css'
import './styles/app.css'
import './styles/landing.css'
import './styles/profile.css'
import './styles/documents.css'

initTheme()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
