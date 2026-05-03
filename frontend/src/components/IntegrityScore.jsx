// src/components/IntegrityScore.jsx
import React from 'react'

export default function IntegrityScore({ score }) {
  const radius = 52
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  const color =
    score >= 80 ? '#4ade80' :
    score >= 60 ? '#fbbf24' :
    '#f87171'

  const label =
    score >= 80 ? 'Strong' :
    score >= 60 ? 'Moderate' :
    'Weak'

  const bgColor =
    score >= 80 ? 'rgba(74,222,128,0.06)' :
    score >= 60 ? 'rgba(251,191,36,0.06)' :
    'rgba(248,113,113,0.06)'

  return (
    <div
      className="flex flex-col items-center justify-center p-6 rounded-2xl border"
      style={{ borderColor: color + '33', background: bgColor }}
    >
      <div className="relative">
        <svg width="128" height="128" className="-rotate-90">
          {/* Background track */}
          <circle
            cx="64" cy="64" r={radius}
            fill="none"
            stroke="#1e1535"
            strokeWidth="8"
          />
          {/* Progress arc */}
          <circle
            cx="64" cy="64" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1s ease', filter: `drop-shadow(0 0 6px ${color})` }}
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-display font-bold" style={{ color }}>
            {Math.round(score)}%
          </span>
          <span className="text-xs font-mono uppercase tracking-widest mt-0.5" style={{ color: color + 'aa' }}>
            {label}
          </span>
        </div>
      </div>

      <div className="mt-3 text-center">
        <p className="text-sm text-gray-400 font-display">Integrity Score</p>
        <p className="text-xs text-gray-600 mt-1">Based on verified claims</p>
      </div>
    </div>
  )
}
