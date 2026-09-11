import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { motion, useReducedMotion } from 'motion/react'
import './styles.css'

const demoStates = ['IDLE', 'LISTENING', 'THINKING', 'EXECUTING', 'SPEAKING']

function App() {
  const [state, setState] = useState('IDLE')
  const [connected, setConnected] = useState(false)
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    let demoTimer
    let source
    try {
      source = new EventSource('/events')
      source.onopen = () => setConnected(true)
      source.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data)
          if (payload.state) setState(String(payload.state).toUpperCase())
        } catch { /* Ignore malformed runtime events. */ }
      }
      source.onerror = () => {
        setConnected(false)
        source?.close()
        demoTimer = window.setInterval(() => setState((current) => demoStates[(demoStates.indexOf(current) + 1) % demoStates.length]), 6500)
      }
    } catch {
      demoTimer = window.setInterval(() => setState((current) => demoStates[(demoStates.indexOf(current) + 1) % demoStates.length]), 6500)
    }
    return () => { source?.close(); if (demoTimer) window.clearInterval(demoTimer) }
  }, [])

  const activate = async () => {
    setState('LISTENING')
    try { await fetch('/command', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ command: 'listen' }) }) } catch { /* UI remains useful without the runtime bridge. */ }
  }

  return (
    <main className={`app state-${state.toLowerCase()}`}>
      <div className="ambient ambient-a" /><div className="ambient ambient-b" /><div className="ambient ambient-c" /><div className="grain" />
      <header className="topbar">
        <div className="brand"><span className="brand-mark">J</span><div><div className="brand-name">J.A.R.V.I.S.</div><div className="brand-sub">HOME BASE</div></div></div>
        <div className="system-pill"><span className={`dot ${connected ? '' : 'offline'}`} /> {connected ? 'RUNTIME CONNECTED' : 'LOCAL UI MODE'}</div>
      </header>
      <section className="hero">
        <motion.div className="core-wrap" animate={reduceMotion ? undefined : { scale: [1, 1.018, 1], rotate: [0, 1, 0] }} transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}>
          <div className="core-glow" /><div className="core-ring ring-one" /><div className="core-ring ring-two" /><div className="core-ring ring-three" />
          <div className="core"><div className="core-inner" /><span>J</span></div>
        </motion.div>
        <motion.div className="status" key={state} initial={reduceMotion ? false : { opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .5 }}>
          <span className="eyebrow">J.A.R.V.I.S. CORE</span><h1>{state}</h1>
          <p>{state === 'IDLE' ? 'Standing by for your command.' : state === 'LISTENING' ? 'Audio input channel active.' : state === 'THINKING' ? 'Processing your request.' : state === 'EXECUTING' ? 'Executing an approved capability.' : 'Voice output channel active.'}</p>
        </motion.div>
      </section>
      <footer className="bottom-grid">
        <div className="glass-card"><span>CORE</span><strong>ONLINE</strong></div>
        <div className="glass-card"><span>STATE</span><strong>{state}</strong></div>
        <button className="glass-card command" onClick={activate}><span>COMMAND</span><strong>ACTIVATE</strong></button>
      </footer>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<App />)
