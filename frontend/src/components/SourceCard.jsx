// src/components/SourceCard.jsx
import React from 'react'

export default function SourceCard({ source, index }) {
  const reliability = Math.round((source.reliability_score || 0.7) * 100)

  return (
    <div
      className="p-4 rounded-xl border border-[#1e1535] bg-[#0d0a1a] hover:border-violet-800 transition-all group"
      style={{ animationDelay: `${index * 0.08}s` }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {/* Source ID badge */}
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-mono bg-[#1a0f30] text-violet-400 border border-violet-900 px-2 py-0.5 rounded">
              {source.id}
            </span>
            {source.url?.includes('arxiv.org') && (
              <span className="text-xs font-mono bg-[#0d1f0f] text-green-400 border border-green-900 px-2 py-0.5 rounded">
                ArXiv
              </span>
            )}
          </div>

          {/* Title */}
          <h4 className="text-sm font-display font-semibold text-gray-200 mb-1 leading-snug line-clamp-2">
            {source.title}
          </h4>

          {/* Meta */}
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-2 font-mono">
            {source.author && source.author !== 'Unknown' && (
              <span>{source.author.split(',')[0]}</span>
            )}
            {source.date && source.date !== 'Unknown' && (
              <>
                <span>·</span>
                <span>{source.date}</span>
              </>
            )}
          </div>

          {/* Summary */}
          <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">
            {source.summary}
          </p>
        </div>
      </div>

      {/* Footer: reliability bar + link */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#1e1535]">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-600">Reliability</span>
          <div className="w-20 h-1.5 bg-[#1e1535] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-1000"
              style={{
                width: `${reliability}%`,
                background: reliability >= 80
                  ? 'linear-gradient(90deg,#16a34a,#4ade80)'
                  : 'linear-gradient(90deg,#7c3aed,#a78bfa)'
              }}
            />
          </div>
          <span className="text-xs font-mono text-gray-500">{reliability}%</span>
        </div>

        {source.url && (
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-violet-500 hover:text-violet-300 font-mono truncate max-w-[140px] transition-colors"
          >
            ↗ View source
          </a>
        )}
      </div>
    </div>
  )
}
