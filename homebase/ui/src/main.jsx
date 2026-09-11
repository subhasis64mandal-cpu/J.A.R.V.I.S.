import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { motion, useReducedMotion } from 'motion/react'
import './styles.css'

const states = ['IDLE', 'LISTENING', 'THINKING', 'SPEAKING']

function App() {
  const [state, setState] = useState('IDLE')
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    const timer = window.setInterval(() => {
      setState((current) => {
        const next = states[(states.indexOf(current) + 1) % states.length]
        return next
      })
    }, 6500)
    return () => window.clearInterval(timer)
  }, [])

  return (
    <main className={`app state-${state.toLowerCase()}`}>
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <div className="ambient ambient-c" />
      <div className="grain" />

      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">J</span>
          <div>
            <div className="brand-name">J.A.R.V.I.S.</div>
            <div className="brand-sub">HOME BASE</div>
          </div>
        </div>
        <div className="system-pill"><span className="dot" /> SYSTEM ONLINE</div>
      </header>

      <section className="hero">
        <motion.div
          className="core-wrap"
          animate={reduceMotion ? undefined : { scale: [1, 1.018, 1], rotate: [0, 1, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="core-glow" />
          <div className="core-ring ring-one" />
          <div className="core-ring ring-two" />
          <div className="core-ring ring-three" />
          <div className="core">
            <div className="core-inner" />
            <span>J</span>
          </div>
        </motion.div>

        <motion.div
          className="status"
          key={state}
          initial={reduceMotion ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="eyebrow">J.A.R.V.I.S. CORE</span>
          <h1>{state}</h1>
          <p>{state === 'IDLE' ? 'Standing by for your command.' : state === 'LISTENING' ? 'Audio input channel active.' : state === 'THINKING' ? 'Processing your request.' : 'Voice output channel active.'}</p>
        </motion.div>
      </section>

      <footer className="bottom-grid">
        <div className="glass-card"><span>CORE</span><strong>ONLINE</strong></div>
        <div className="glass-card"><span>LATENCY</span><strong>12 MS</strong></div>
        <button className="glass-card command" onClick={() => setState('LISTENING')}><span>COMMAND</span><strong>ACTIVATE</strong></button>
      </footer>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<App />)
