// src/components/LiveLog.jsx
import React, { useEffect, useRef } from 'react'

const STATE_COLORS = {
  IDLE: 'text-gray-400',
  CONNECTED: 'text-blue-400',
  RESEARCHING: 'text-violet-400',
  EMBEDDING: 'text-indigo-400',
  VERIFYING: 'text-yellow-400',
  DRAFTING: 'text-cyan-400',
  REPORTING: 'text-pink-400',
  COMPLETE: 'text-green-400',
  ERROR: 'text-red-400',
}

const STATE_ICONS = {
  IDLE: '◯',
  CONNECTED: '◉',
  RESEARCHING: '⟳',
  EMBEDDING: '⬡',
  VERIFYING: '◈',
  DRAFTING: '✦',
  REPORTING: '⊞',
  COMPLETE: '✓',
  ERROR: '✗',
}

export default function LiveLog({ logs, isRunning }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  if (logs.length === 0 && !isRunning) return null

  return (
    <div className="rounded-xl border border-[#1e1535] bg-[#0a0716] overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-[#1e1535] bg-[#0d0a1a]">
        <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-violet-500 pulse-ring' : 'bg-gray-600'}`} />
        <span className="text-xs font-mono text-gray-500 uppercase tracking-widest">
          Research Trail
        </span>
        <span className="ml-auto text-xs font-mono text-gray-600">
          {logs.length} events
        </span>
      </div>

      {/* Log entries */}
      <div className="p-4 space-y-1 max-h-64 overflow-y-auto font-mono text-xs">
        {logs.map((log) => (
          <div
            key={log.id}
            className="flex items-start gap-3 py-1 opacity-0 animate-[fadeIn_0.3s_ease_forwards]"
            style={{ animation: 'fadeSlideIn 0.25s ease forwards' }}
          >
            <span className="text-gray-600 flex-shrink-0 w-16">{log.timestamp}</span>
            <span className={`flex-shrink-0 ${STATE_COLORS[log.state] || 'text-gray-400'}`}>
              {STATE_ICONS[log.state] || '·'}
            </span>
            <span className={`${STATE_COLORS[log.state] || 'text-gray-300'} leading-relaxed`}>
              {log.message}
            </span>
          </div>
        ))}

        {isRunning && (
          <div className="flex items-center gap-3 py-1">
            <span className="text-gray-600 flex-shrink-0 w-16">now</span>
            <span className="text-violet-400 flex-shrink-0">
              <span className="inline-block animate-spin">⟳</span>
            </span>
            <span className="text-violet-300 cursor-blink">Processing</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateX(-8px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  )
}
