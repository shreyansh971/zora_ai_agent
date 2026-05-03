// src/hooks/useVera.js
// Custom hook that manages the WebSocket connection to the Vera pipeline

import { useState, useRef, useCallback } from 'react'

const WS_URL = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:8000/ws/research`

export function useVera() {
  const [state, setState] = useState('IDLE')
  const [logs, setLogs] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const wsRef = useRef(null)

  const addLog = useCallback((message, state) => {
    setLogs(prev => [...prev, {
      id: Date.now() + Math.random(),
      message,
      state,
      timestamp: new Date().toLocaleTimeString(),
    }])
  }, [])

  const runResearch = useCallback(async ({ topic, draft_text, user_id = 'user' }) => {
    if (isRunning) return

    // Reset
    setLogs([])
    setResult(null)
    setError(null)
    setIsRunning(true)
    setState('CONNECTING')

    try {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        setState('CONNECTED')
        addLog('Connection established with Vera...', 'CONNECTED')
        ws.send(JSON.stringify({ topic, draft_text, user_id }))
      }

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data)

        if (msg.type === 'progress') {
          setState(msg.state)
          addLog(msg.message, msg.state)
        } else if (msg.type === 'complete') {
          setState('COMPLETE')
          setResult(msg)
          addLog('✅ Pipeline complete!', 'COMPLETE')
          setIsRunning(false)
        } else if (msg.type === 'error') {
          setState('ERROR')
          setError(msg.message)
          addLog(`❌ Error: ${msg.message}`, 'ERROR')
          setIsRunning(false)
        }
      }

      ws.onerror = () => {
        setState('ERROR')
        setError('WebSocket connection failed. Is the backend running on port 8000?')
        addLog('Connection error — check that backend is running.', 'ERROR')
        setIsRunning(false)
      }

      ws.onclose = () => {
        if (state !== 'COMPLETE') {
          addLog('Connection closed.', 'IDLE')
        }
      }
    } catch (err) {
      setState('ERROR')
      setError(err.message)
      setIsRunning(false)
    }
  }, [isRunning, addLog, state])

  const cancel = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsRunning(false)
    setState('IDLE')
    addLog('Research cancelled.', 'IDLE')
  }, [addLog])

  return { state, logs, result, error, isRunning, runResearch, cancel }
}
