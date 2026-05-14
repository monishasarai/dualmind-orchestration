import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'

const Home = () => {
  return (
    <div className="min-h-screen bg-dark-bg">
      <Navbar />
      
      <div className="flex flex-col items-center justify-center min-h-screen px-6 pt-20">
        <div className="max-w-4xl mx-auto text-center">
          {/* Icon */}
          <div className="mb-12">
            <div className="w-24 h-24 mx-auto flex items-center justify-center">
              <span className="text-7xl">🧠</span>
            </div>
          </div>

          {/* Hero heading */}
          <h1 className="bg-gradient-to-r from-cyan-400 to-blue-500 
                     bg-clip-text text-transparent 
                     hover:opacity-90 transition-all duration-200 text-5xl md:text-7xl font-semibold mb-6 text-text-primary">
            DualMind
          </h1>
          
          <p className="text-2xl md:text-3xl text-text-primary mb-4 font-light">
            Discover, Learn, and Think Smarter.
          </p>
          
          <p className="text-lg md:text-xl text-text-secondary mb-12 max-w-2xl mx-auto">
            Your intelligent AI companion for deep insights.
          </p>

          {/* CTA Button */}
          <Link
            to="/chat"
            className="inline-block px-8 py-4 border border-aqua text-aqua bg-transparent font-medium rounded-lg transition-all duration-200 ease-in-out hover:bg-aqua-hover"
          >
            Try Now
          </Link>

          {/* Feature highlights */}
          <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <div className="p-6 rounded-lg border border-dark-border bg-dark-surface">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold text-text-primary mb-2">Deep Research</h3>
              <p className="text-text-secondary">Access comprehensive information from multiple sources</p>
            </div>
            
            <div className="p-6 rounded-lg border border-dark-border bg-dark-surface">
              <div className="text-4xl mb-4">💡</div>
              <h3 className="text-xl font-semibold text-text-primary mb-2">Smart Insights</h3>
              <p className="text-text-secondary">Get intelligent analysis and actionable recommendations</p>
            </div>
            
            <div className="p-6 rounded-lg border border-dark-border bg-dark-surface">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold text-text-primary mb-2">Fast & Accurate</h3>
              <p className="text-text-secondary">Real-time responses with verified information</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
