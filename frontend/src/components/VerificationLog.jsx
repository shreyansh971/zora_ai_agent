// src/components/VerificationLog.jsx
import React, { useState } from 'react'

const STATUS_CONFIG = {
  Verified:      { cls: 'badge-verified',      icon: '✓', label: 'Verified' },
  Hallucinated:  { cls: 'badge-hallucinated',  icon: '✗', label: 'Hallucinated' },
  Partial:       { cls: 'badge-partial',       icon: '~', label: 'Partial' },
  Unverifiable:  { cls: 'badge-unverifiable',  icon: '?', label: 'Unknown' },
}

const BORDER_COLORS = {
  Verified:     'border-l-green-600',
  Hallucinated: 'border-l-red-600',
  Partial:      'border-l-yellow-600',
  Unverifiable: 'border-l-gray-600',
}

export default function VerificationLog({ chunks }) {
  const [filter, setFilter] = useState('All')

  const filters = ['All', 'Verified', 'Hallucinated', 'Partial', 'Unverifiable']
  const counts = {}
  filters.forEach(f => {
    counts[f] = f === 'All' ? chunks.length : chunks.filter(c => c.status === f).length
  })

  const visible = filter === 'All' ? chunks : chunks.filter(c => c.status === filter)

  return (
    <div className="space-y-4">
      {/* Filter tabs */}
      <div className="flex flex-wrap gap-2">
        {filters.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-lg text-xs font-mono font-medium border transition-all ${
              filter === f
                ? 'bg-violet-900 border-violet-600 text-violet-200'
                : 'bg-[#0d0a1a] border-[#1e1535] text-gray-500 hover:border-violet-800 hover:text-gray-300'
            }`}
          >
            {f} <span className="opacity-60">({counts[f]})</span>
          </button>
        ))}
      </div>

      {/* Claim cards */}
      <div className="space-y-2">
        {visible.map((chunk, i) => {
          const cfg = STATUS_CONFIG[chunk.status] || STATUS_CONFIG.Unverifiable
          const borderCls = BORDER_COLORS[chunk.status] || 'border-l-gray-600'

          return (
            <div
              key={i}
              className={`p-3 rounded-r-xl rounded-bl-xl border-l-2 bg-[#0d0a1a] border border-[#1e1535] ${borderCls}`}
            >
              <div className="flex items-start gap-3">
                <span className={`text-xs font-mono px-2 py-0.5 rounded flex-shrink-0 ${cfg.cls}`}>
                  {cfg.icon} {cfg.label}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-300 leading-relaxed">{chunk.chunk}</p>

                  <div className="flex items-center gap-3 mt-2 flex-wrap">
                    {chunk.source_ref && (
                      <span className="text-xs font-mono text-violet-500">
                        → [{chunk.source_ref}]
                      </span>
                    )}
                    {chunk.confidence > 0 && (
                      <span className="text-xs font-mono text-gray-600">
                        confidence: {Math.round(chunk.confidence * 100)}%
                      </span>
                    )}
                  </div>

                  {chunk.suggestion && (
                    <div className="mt-2 p-2 rounded-lg bg-[#1c1409] border border-yellow-900/50">
                      <p className="text-xs text-yellow-400">
                        💡 <span className="font-semibold">Suggestion:</span> {chunk.suggestion}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {visible.length === 0 && (
        <div className="text-center py-8 text-gray-600 font-mono text-sm">
          No claims with status "{filter}"
        </div>
      )}
    </div>
  )
}
