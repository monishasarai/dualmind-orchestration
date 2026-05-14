import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { ThemeProvider } from './contexts/ThemeContext'
import { ToastProvider } from './contexts/ToastContext'
import { AuthProvider } from './contexts/AuthContext'

const Home   = lazy(() => import('./pages/Home'))
const Chat   = lazy(() => import('./pages/Chat'))
const Login  = lazy(() => import('./pages/Login'))
const Signup = lazy(() => import('./pages/Signup'))

const PageLoader = () => (
  <div className="h-screen flex items-center justify-center">
    <div className="flex gap-2">
      <span className="typing-dot w-2.5 h-2.5 rounded-full bg-neon-blue inline-block" />
      <span className="typing-dot w-2.5 h-2.5 rounded-full bg-neon-purple inline-block" />
      <span className="typing-dot w-2.5 h-2.5 rounded-full bg-neon-pink inline-block" />
    </div>
  </div>
)

const App = () => (
  <ThemeProvider>
    <ToastProvider>
      <AuthProvider>
        <div className="animated-bg" />
        <BrowserRouter>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/"       element={<Home />} />
              <Route path="/chat"   element={<Chat />} />
              <Route path="/login"  element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="*"       element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AuthProvider>
    </ToastProvider>
  </ThemeProvider>
)

export default App
