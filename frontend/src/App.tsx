import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Chat from './pages/Chat'
import { ThemeProvider } from './contexts/ThemeContext'

const App = () => {
  return (
    <ThemeProvider>
      <div className="animated-bg"></div>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
