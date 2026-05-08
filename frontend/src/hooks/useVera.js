// src/hooks/useVera.js
// Uses HTTP polling instead of WebSocket — works on all free hosting platforms

import { useState, useRef, useCallback } from 'react'

const getBackendUrl = () => {
  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL.replace(/\/$/, '')
  }
  return 'http://localhost:8000'
}

export function useVera() {
  const [state, setState] = useState('IDLE')
  const [logs, setLogs] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const cancelRef = useRef(false)

  const addLog = useCallback((message, logState) => {
    setLogs(prev => [...prev, {
      id: Date.now() + Math.random(),
      message,
      state: logState,
      timestamp: new Date().toLocaleTimeString(),
    }])
  }, [])

  const runResearch = useCallback(async ({ topic, draft_text, user_id = 'user' }) => {
    if (isRunning) return
    cancelRef.current = false
    setLogs([])
    setResult(null)
    setError(null)
    setIsRunning(true)
    setState('RESEARCHING')

    const backendUrl = getBackendUrl()

    try {
      addLog('Connecting to Zora backend...', 'CONNECTING')

      // Wake up the backend first
      try {
        await fetch(`${backendUrl}/health`, { method: 'GET' })
        addLog('Backend is online ✓', 'CONNECTED')
      } catch (e) {
        addLog('Waking up backend (may take 30s on free tier)...', 'CONNECTING')
        await new Promise(r => setTimeout(r, 5000))
      }

      if (cancelRef.current) return

      addLog(`Starting research on: "${topic}"`, 'RESEARCHING')
      setState('RESEARCHING')

      // Call the REST API endpoint
      const response = await fetch(`${backendUrl}/api/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, draft_text, user_id }),
        signal: AbortSignal.timeout(120000), // 2 min timeout
      })

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || `Server error: ${response.status}`)
      }

      if (cancelRef.current) return

      // Simulate progress updates while waiting
      const progressSteps = [
        { state: 'RESEARCHING', msg: 'Searching ArXiv and web sources...' },
        { state: 'EMBEDDING',   msg: 'Embedding sources into vector memory...' },
        { state: 'VERIFYING',   msg: 'Verifying claims against sources...' },
        { state: 'DRAFTING',    msg: 'Generating grounded draft...' },
        { state: 'REPORTING',   msg: 'Compiling Research Receipt...' },
      ]

      // Show fake progress while request is in flight
      let stepIdx = 0
      const progressInterval = setInterval(() => {
        if (stepIdx < progressSteps.length && !cancelRef.current) {
          const step = progressSteps[stepIdx]
          setState(step.state)
          addLog(step.msg, step.state)
          stepIdx++
        }
      }, 8000)

      const data = await response.json()
      clearInterval(progressInterval)

      if (cancelRef.current) return

      setState('COMPLETE')
      setResult({
        ...data,
        type: 'complete',
      })
      addLog('✅ Pipeline complete!', 'COMPLETE')
    } catch (err) {
      if (cancelRef.current) return
      setState('ERROR')
      const msg = err.name === 'TimeoutError'
        ? 'Request timed out (backend may be sleeping). Please try again in 30 seconds.'
        : err.message
      setError(msg)
      addLog(`❌ ${msg}`, 'ERROR')
    } finally {
      setIsRunning(false)
    }
  }, [isRunning, addLog])

  const cancel = useCallback(() => {
    cancelRef.current = true
    setIsRunning(false)
    setState('IDLE')
    addLog('Research cancelled.', 'IDLE')
  }, [addLog])

  return { state, logs, result, error, isRunning, runResearch, cancel }
}