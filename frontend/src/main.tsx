import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { BackendWakeGate } from './components/layout/BackendWakeGate.tsx'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BackendWakeGate>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </BackendWakeGate>
  </StrictMode>,
)
