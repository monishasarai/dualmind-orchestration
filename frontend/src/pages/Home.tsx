import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'

const Home = () => {
  return (
    <div className="min-h-screen bg-transparent">
      <Navbar />
      
      <div className="flex flex-col items-center justify-center min-h-screen px-6 pt-20">
        <div className="max-w-4xl mx-auto text-center relative z-10">
          {/* Glowing Orb behind icon */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-neon-blue/20 rounded-full blur-[100px] -z-10"></div>
          
          {/* Icon */}
          <div className="mb-12 animate-float">
            <div className="w-32 h-32 mx-auto flex items-center justify-center glass rounded-full shadow-neon-blue">
              <span className="text-7xl">🧠</span>
            </div>
          </div>

          {/* Hero heading */}
          <h1 className="bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink 
                     bg-clip-text text-transparent 
                     hover:opacity-90 transition-all duration-200 text-6xl md:text-8xl font-bold mb-6 tracking-tight animate-pulse-glow">
            DualMind
          </h1>
          
          <p className="text-2xl md:text-4xl text-text-primary mb-4 font-light tracking-wide">
            Discover, Learn, and Think Smarter.
          </p>
          
          <p className="text-lg md:text-xl text-text-secondary mb-12 max-w-2xl mx-auto">
            Your intelligent AI companion for deep insights.
          </p>

          {/* CTA Button */}
          <Link
            to="/chat"
            className="inline-block px-10 py-5 border-2 border-neon-blue text-neon-blue bg-transparent font-bold text-lg rounded-xl transition-all duration-300 ease-in-out hover:bg-neon-blue/10 hover:shadow-neon-blue animate-pulse-glow"
          >
            Initialize Connection
          </Link>

          {/* Feature highlights */}
          <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="p-8 rounded-2xl glass-panel hover:-translate-y-2 transition-transform duration-300 hover:shadow-neon-blue group">
              <div className="text-5xl mb-6 group-hover:scale-110 transition-transform">🔍</div>
              <h3 className="text-xl font-bold text-text-primary mb-3">Deep Research</h3>
              <p className="text-text-secondary leading-relaxed">Access comprehensive information from multiple sources</p>
            </div>
            
            <div className="p-8 rounded-2xl glass-panel hover:-translate-y-2 transition-transform duration-300 hover:shadow-neon-purple group">
              <div className="text-5xl mb-6 animate-pulse group-hover:scale-110 transition-transform">💡</div>
              <h3 className="text-xl font-bold text-text-primary mb-3">Smart Insights</h3>
              <p className="text-text-secondary leading-relaxed">Get intelligent analysis and actionable recommendations</p>
            </div>
            
            <div className="p-8 rounded-2xl glass-panel hover:-translate-y-2 transition-transform duration-300 hover:shadow-neon-pink group">
              <div className="text-5xl mb-6 group-hover:scale-110 transition-transform">⚡</div>
              <h3 className="text-xl font-bold text-text-primary mb-3">Fast & Accurate</h3>
              <p className="text-text-secondary leading-relaxed">Real-time responses with verified information</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
