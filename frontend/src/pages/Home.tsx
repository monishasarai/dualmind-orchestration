import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain, Zap, Shield, Globe, Code2, BarChart3,
  ChevronDown, ChevronRight, Star,
  ArrowRight, Check, Sparkles, MessageSquare, Cpu, ExternalLink
} from 'lucide-react'
import Navbar from '../components/Navbar'

// ── Shared animation variants ──────────────────────────────────────────────────

const fadeUp = {
  hidden: { opacity: 0, y: 36 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' as const } },
}

// ── Data ───────────────────────────────────────────────────────────────────────

const features = [
  { icon: <Brain size={28} />, title: 'Dual-Agent Reasoning', desc: 'Generator + Discriminator architecture ensures every response is planned, verified, and refined before delivery.', color: 'neon-blue' },
  { icon: <Zap size={28} />, title: 'Real-Time Streaming', desc: 'Watch answers appear token-by-token with sub-second latency via Server-Sent Events.', color: 'neon-purple' },
  { icon: <Code2 size={28} />, title: 'Code Intelligence', desc: 'Syntax-highlighted code blocks with copy controls, language detection, and inline explanations.', color: 'neon-pink' },
  { icon: <Globe size={28} />, title: 'Multi-Source Research', desc: 'Pulls from arXiv, PubMed, Wikipedia, news feeds, and semantic scholar in a single query.', color: 'neon-blue' },
  { icon: <Shield size={28} />, title: 'Verified Outputs', desc: 'Every plan is scored by the Discriminator before execution — no hallucinated facts.', color: 'neon-purple' },
  { icon: <BarChart3 size={28} />, title: 'Rich Visualisations', desc: 'Auto-generated charts, data plots, and structured tables from raw data.', color: 'neon-pink' },
]

const steps = [
  { icon: <MessageSquare size={22} />, label: 'User Query', desc: 'You send a message or upload a file.' },
  { icon: <Brain size={22} />, label: 'Generator', desc: 'Plans a multi-step execution strategy.' },
  { icon: <Shield size={22} />, label: 'Discriminator', desc: 'Scores and approves the plan.' },
  { icon: <Cpu size={22} />, label: 'Tool Execution', desc: 'Runs search, code, and data tools.' },
  { icon: <Sparkles size={22} />, label: 'Response', desc: 'Streams the verified answer to you.' },
]

const testimonials = [
  { name: 'Aisha Rahman', role: 'ML Research Lead', quote: 'DualMind replaced three separate tools for me. The dual-agent verification is a game-changer for research accuracy.', stars: 5 },
  { name: 'Carlos Mendez', role: 'Senior Full-Stack Engineer', quote: 'The code intelligence is insane. It explains, refactors, and documents in one shot. My PR review time dropped 40%.', stars: 5 },
  { name: 'Priya Nair', role: 'Product Manager', quote: "Finally an AI that doesn't hallucinate. The Discriminator layer gives me confidence to share outputs directly with stakeholders.", stars: 5 },
]

const pricing = [
  {
    name: 'Free', price: '$0', period: '/month',
    desc: 'Perfect for exploring DualMind.',
    features: ['50 messages / day', 'Basic tool access', 'Chat history (7 days)', 'Community support'],
    cta: 'Get Started', highlight: false,
  },
  {
    name: 'Pro', price: '$19', period: '/month',
    desc: 'For power users and professionals.',
    features: ['Unlimited messages', 'All tools + file upload', 'Unlimited chat history', 'Priority support', 'API access', 'Export conversations'],
    cta: 'Start Free Trial', highlight: true,
  },
]

const faqs = [
  { q: 'What is the dual-agent architecture?', a: 'DualMind uses two AI agents: a Generator that creates plans and responses, and a Discriminator that scores and validates them. Only approved plans are executed, dramatically reducing errors.' },
  { q: 'How is DualMind different from ChatGPT?', a: 'Unlike single-model chatbots, DualMind orchestrates multiple specialised tools (search, code, data analysis) and verifies every output before showing it to you.' },
  { q: 'Can I upload files?', a: 'Yes. You can upload PDFs, images (PNG/JPEG), and documents. DualMind will parse, analyse, and answer questions about the content.' },
  { q: 'Is my data private?', a: 'Conversations are stored securely in your personal account. We never use your data to train models. You can export or delete your history at any time.' },
  { q: 'Does it support real-time streaming?', a: 'Yes. Responses stream token-by-token via Server-Sent Events so you see the answer forming in real time, just like watching someone type.' },
  { q: 'What tools does DualMind have access to?', a: 'arXiv summariser, PubMed search, Wikipedia, news fetcher, semantic scholar, sentiment analyser, data plotter, PDF parser, document writer, and a QA engine.' },
]

// ── Sub-components ─────────────────────────────────────────────────────────────

const GlowOrb = ({ className }: { className: string }) => (
  <div className={`absolute rounded-full blur-[120px] pointer-events-none ${className}`} />
)

const StarRating = ({ n }: { n: number }) => (
  <div className="flex gap-0.5">
    {Array.from({ length: n }).map((_, i) => (
      <Star key={i} size={14} className="fill-yellow-400 text-yellow-400" />
    ))}
  </div>
)

/** Section heading — always animates in from below when it enters the viewport */
const SectionHeading = ({ children }: { children: React.ReactNode }) => (
  <motion.div
    className="text-center mb-16"
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true, amount: 0.3 }}
    variants={fadeUp}
  >
    {children}
  </motion.div>
)
const FaqItem = ({ q, a }: { q: string; a: string }) => {
  const [open, setOpen] = useState(false)
  return (
    <div className="glass-panel rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-6 py-5 text-left gap-4 hover:bg-white/5 transition-colors"
      >
        <span className="font-semibold text-text-primary">{q}</span>
        <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.25 }}>
          <ChevronDown size={18} className="text-text-secondary flex-shrink-0" />
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="answer"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            style={{ overflow: 'hidden' }}
          >
            <p className="px-6 pb-5 text-text-secondary leading-relaxed">{a}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────────

const Home = () => (
  <div className="min-h-screen bg-transparent text-text-primary">
    <Navbar />

    {/* ── HERO ── */}
    <section id="hero" className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-24 pb-16 overflow-hidden">
      <GlowOrb className="w-[600px] h-[600px] bg-neon-blue/10 top-[-100px] left-[-200px]" />
      <GlowOrb className="w-[500px] h-[500px] bg-neon-purple/10 bottom-[-100px] right-[-150px]" />

      <div className="max-w-5xl mx-auto text-center relative z-10">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="inline-flex items-center gap-2 glass rounded-full px-4 py-2 text-sm text-neon-blue border border-neon-blue/30 mb-8"
        >
          <Sparkles size={14} />
          <span>Dual-Agent AI Platform — Now in Beta</span>
        </motion.div>

        {/* Floating brain */}
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-10"
        >
          <motion.div
            animate={{ y: [0, -14, 0] }}
            transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
            className="w-28 h-28 mx-auto flex items-center justify-center glass rounded-full shadow-neon-blue"
          >
            <span className="text-6xl">🧠</span>
          </motion.div>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="text-7xl md:text-9xl font-extrabold tracking-tight mb-6 neon-text"
        >
          DualMind
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.45 }}
          className="text-2xl md:text-3xl text-text-primary font-light mb-4 tracking-wide"
        >
          Think Deeper. Reason Smarter.
        </motion.p>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.55 }}
          className="text-lg text-text-secondary max-w-2xl mx-auto mb-12 leading-relaxed"
        >
          The first AI platform with a built-in Discriminator that verifies every answer before you see it.
          Powered by a dual-agent architecture for research, code, and complex reasoning.
        </motion.p>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.65 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Link
            to="/signup"
            className="group inline-flex items-center gap-2 px-10 py-4 rounded-xl bg-neon-blue/10 border-2 border-neon-blue text-neon-blue font-bold text-lg transition-all duration-300 hover:bg-neon-blue/20 hover:shadow-neon-blue"
          >
            Try Now
            <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
          </Link>
          <a
            href="#how-it-works"
            className="inline-flex items-center gap-2 px-10 py-4 rounded-xl glass border border-white/10 text-text-primary font-semibold text-lg transition-all duration-300 hover:bg-white/5"
          >
            How It Works
          </a>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-20 grid grid-cols-3 gap-8 max-w-lg mx-auto"
        >
          {[['10+', 'AI Tools'], ['2-Agent', 'Verification'], ['<1s', 'Response']].map(([val, label]) => (
            <div key={label} className="text-center">
              <div className="text-2xl font-bold neon-text">{val}</div>
              <div className="text-xs text-text-secondary mt-1">{label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>

    {/* ── FEATURES ── */}
    <section id="features" className="py-28 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionHeading>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Everything you need to <span className="neon-text">think at scale</span>
          </h2>
          <p className="text-text-secondary text-lg max-w-2xl mx-auto">
            Six core capabilities that make DualMind the most reliable AI platform for serious work.
          </p>
        </SectionHeading>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.15 }}
              transition={{ duration: 0.55, delay: i * 0.08, ease: 'easeOut' }}
              whileHover={{ y: -6, transition: { duration: 0.2 } }}
              className="glass-panel rounded-2xl p-7 group cursor-default transition-shadow duration-300 hover:shadow-neon-blue"
            >
              <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-5 bg-neon-blue/10 text-neon-blue group-hover:scale-110 transition-transform duration-200">
                {f.icon}
              </div>
              <h3 className="text-lg font-bold text-text-primary mb-2">{f.title}</h3>
              <p className="text-text-secondary text-sm leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>

    {/* ── HOW IT WORKS ── */}
    <section id="how-it-works" className="py-28 px-6">
      <div className="max-w-5xl mx-auto">
        <SectionHeading>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            How <span className="neon-text">DualMind</span> Works
          </h2>
          <p className="text-text-secondary text-lg max-w-xl mx-auto">
            A five-stage pipeline that plans, verifies, executes, and delivers.
          </p>
        </SectionHeading>

        <div className="relative">
          {/* Connector line */}
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true, amount: 0.5 }}
            transition={{ duration: 1, ease: 'easeInOut' }}
            style={{ originX: 0 }}
            className="hidden md:block absolute top-10 left-[10%] right-[10%] h-px bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink opacity-40"
          />

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            {steps.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.2 }}
                transition={{ duration: 0.5, delay: i * 0.12, ease: 'easeOut' }}
                className="flex flex-col items-center text-center"
              >
                <div className="w-20 h-20 rounded-full glass flex items-center justify-center mb-4 shadow-neon-blue text-neon-blue relative z-10">
                  {s.icon}
                  <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-neon-blue text-[10px] font-bold text-black flex items-center justify-center">
                    {i + 1}
                  </span>
                </div>
                <h4 className="font-bold text-text-primary mb-1">{s.label}</h4>
                <p className="text-text-secondary text-xs leading-relaxed">{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>

    {/* ── TESTIMONIALS ── */}
    <section id="testimonials" className="py-28 px-6">
      <div className="max-w-5xl mx-auto">
        <SectionHeading>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Trusted by <span className="neon-text">builders</span>
          </h2>
        </SectionHeading>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.55, delay: i * 0.12, ease: 'easeOut' }}
              className="glass-panel rounded-2xl p-7 flex flex-col gap-4"
            >
              <StarRating n={t.stars} />
              <p className="text-text-secondary text-sm leading-relaxed flex-1">"{t.quote}"</p>
              <div className="flex items-center gap-3 pt-2 border-t border-white/5">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center text-white text-sm font-bold">
                  {t.name[0]}
                </div>
                <div>
                  <p className="text-sm font-semibold text-text-primary">{t.name}</p>
                  <p className="text-xs text-text-secondary">{t.role}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>

    {/* ── PRICING ── */}
    <section id="pricing" className="py-28 px-6">
      <div className="max-w-4xl mx-auto">
        <SectionHeading>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Simple, <span className="neon-text">transparent</span> pricing
          </h2>
          <p className="text-text-secondary text-lg">Start free. Upgrade when you're ready.</p>
        </SectionHeading>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {pricing.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.55, delay: i * 0.15, ease: 'easeOut' }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
              className={`rounded-2xl p-8 flex flex-col gap-6 relative overflow-hidden ${
                plan.highlight
                  ? 'border-2 border-neon-blue shadow-neon-blue glass'
                  : 'glass-panel'
              }`}
            >
              {plan.highlight && (
                <div className="absolute top-4 right-4 text-xs font-bold px-3 py-1 rounded-full bg-neon-blue/20 text-neon-blue border border-neon-blue/40">
                  Most Popular
                </div>
              )}
              <div>
                <h3 className="text-xl font-bold text-text-primary mb-1">{plan.name}</h3>
                <p className="text-text-secondary text-sm">{plan.desc}</p>
              </div>
              <div className="flex items-end gap-1">
                <span className="text-5xl font-extrabold neon-text">{plan.price}</span>
                <span className="text-text-secondary mb-2">{plan.period}</span>
              </div>
              <ul className="space-y-3 flex-1">
                {plan.features.map(f => (
                  <li key={f} className="flex items-center gap-3 text-sm text-text-secondary">
                    <Check size={15} className="text-neon-blue flex-shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                to="/signup"
                className={`w-full text-center py-3 rounded-xl font-bold transition-all duration-300 ${
                  plan.highlight
                    ? 'bg-neon-blue/10 border-2 border-neon-blue text-neon-blue hover:bg-neon-blue/20 hover:shadow-neon-blue'
                    : 'glass border border-white/10 text-text-primary hover:bg-white/5'
                }`}
              >
                {plan.cta}
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>

    {/* ── FAQ ── */}
    <section id="faq" className="py-28 px-6">
      <div className="max-w-3xl mx-auto">
        <SectionHeading>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Frequently asked <span className="neon-text">questions</span>
          </h2>
        </SectionHeading>

        <motion.div
          className="space-y-3"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          variants={{
            hidden: {},
            visible: { transition: { staggerChildren: 0.08 } },
          }}
        >
          {faqs.map(faq => (
            <motion.div
              key={faq.q}
              variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45 } } }}
            >
              <FaqItem q={faq.q} a={faq.a} />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>

    {/* ── CTA BANNER ── */}
    <section className="py-24 px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.94 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="max-w-3xl mx-auto text-center glass rounded-3xl p-14 border border-neon-blue/20 shadow-neon-blue relative overflow-hidden"
      >
        <GlowOrb className="w-64 h-64 bg-neon-blue/10 top-[-60px] left-[-60px]" />
        <GlowOrb className="w-64 h-64 bg-neon-purple/10 bottom-[-60px] right-[-60px]" />
        <h2 className="text-4xl font-extrabold mb-4 relative z-10">
          Ready to think <span className="neon-text">smarter</span>?
        </h2>
        <p className="text-text-secondary mb-8 relative z-10">
          Join thousands of researchers, engineers, and creators using DualMind every day.
        </p>
        <Link
          to="/signup"
          className="relative z-10 inline-flex items-center gap-2 px-10 py-4 rounded-xl bg-neon-blue/10 border-2 border-neon-blue text-neon-blue font-bold text-lg transition-all duration-300 hover:bg-neon-blue/20 hover:shadow-neon-blue"
        >
          Start for Free <ArrowRight size={20} />
        </Link>
      </motion.div>
    </section>

    {/* ── FOOTER ── */}
    <footer className="border-t border-white/5 py-12 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-extrabold neon-text">DualMind</span>
            <span className="text-text-secondary text-sm">© {new Date().getFullYear()} All rights reserved.</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-text-secondary">
            <a href="#features" className="hover:text-neon-blue transition-colors">Features</a>
            <a href="#pricing" className="hover:text-neon-blue transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-neon-blue transition-colors">FAQ</a>
            <Link to="/chat" className="hover:text-neon-blue transition-colors">Chat</Link>
          </div>
          <div className="flex items-center gap-4">
            {['Twitter', 'GitHub', 'LinkedIn'].map(name => (
              <a key={name} href="#" className="text-text-secondary hover:text-neon-blue transition-colors text-xs">
                <ExternalLink size={16} />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  </div>
)

export default Home
