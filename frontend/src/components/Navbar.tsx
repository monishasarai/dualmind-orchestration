import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-bg border-b border-dark-border">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center">
        <Link
          to="/"
          className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 
                     bg-clip-text text-transparent 
                     hover:opacity-90 transition-all duration-200"
        >
          DualMind
        </Link>
      </div>
    </nav>
  )
}

export default Navbar
