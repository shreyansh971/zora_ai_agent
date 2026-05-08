// src/hooks/useVera.js
import { useState, useRef, useCallback } from 'react'

const getWsUrl = () => {
  if (import.meta.env.VITE_BACKEND_URL) {
    const base = import.meta.env.VITE_BACKEND_URL
      .replace('https://', 'wss://')
      .replace('http://', 'ws://')
      .replace(/\/$/, '')
    return `${base}/ws/research`
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.hostname}:8000/ws/research`
}

export function useVera() {
  const [state, setState] = useState('IDLE')
  const [logs, setLogs] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const wsRef = useRef(null)

  const addLog = useCallback((message, logState) => {
    setLogs(prev => [...prev, {
      id: Date.now() + Math.random(),
      message, state: logState,
      timestamp: new Date().toLocaleTimeString(),
    }])
  }, [])

  const runResearch = useCallback(async ({ topic, draft_text, user_id = 'user' }) => {
    if (isRunning) return
    setLogs([]); setResult(null); setError(null)
    setIsRunning(true); setState('CONNECTING')
    try {
      const wsUrl = getWsUrl()
      console.log('Connecting to:', wsUrl)
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      ws.onopen = () => {
        setState('CONNECTED')
        addLog('Connection established with Zora...', 'CONNECTED')
        ws.send(JSON.stringify({ topic, draft_text, user_id }))
      }
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data)
        if (msg.type === 'progress') { setState(msg.state); addLog(msg.message, msg.state) }
        else if (msg.type === 'complete') { setState('COMPLETE'); setResult(msg); addLog('✅ Pipeline complete!', 'COMPLETE'); setIsRunning(false) }
        else if (msg.type === 'error') { setState('ERROR'); setError(msg.message); addLog(`❌ ${msg.message}`, 'ERROR'); setIsRunning(false) }
      }
      ws.onerror = () => {
        setState('ERROR')
        setError(import.meta.env.VITE_BACKEND_URL
          ? `Cannot connect to backend. Make sure Render service is running at ${import.meta.env.VITE_BACKEND_URL}`
          : 'Set VITE_BACKEND_URL in Vercel environment variables pointing to your Render backend.')
        setIsRunning(false)
      }
      ws.onclose = () => { if (state !== 'COMPLETE') addLog('Connection closed.', 'IDLE') }
    } catch (err) { setState('ERROR'); setError(err.message); setIsRunning(false) }
  }, [isRunning, addLog, state])

  const cancel = useCallback(() => {
    if (wsRef.current) { wsRef.current.close(); wsRef.current = null }
    setIsRunning(false); setState('IDLE')
    addLog('Research cancelled.', 'IDLE')
  }, [addLog])

  return { state, logs, result, error, isRunning, runResearch, cancel }
}