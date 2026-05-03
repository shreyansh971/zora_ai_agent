// src/App.jsx — ZORA: The Integrity Agent
import React, { useState } from 'react'
import { useVera } from './hooks/useVera'
import LiveLog from './components/LiveLog'
import IntegrityScore from './components/IntegrityScore'
import SourceCard from './components/SourceCard'
import VerificationLog from './components/VerificationLog'

const PIPELINE_STEPS = [
  { key: 'RESEARCHING', label: 'Research', icon: '🔍' },
  { key: 'EMBEDDING',   label: 'Memory',   icon: '🧠' },
  { key: 'VERIFYING',   label: 'Verify',   icon: '✓' },
  { key: 'DRAFTING',    label: 'Draft',    icon: '✍️' },
  { key: 'REPORTING',   label: 'Receipt',  icon: '📜' },
]
const STEP_ORDER = ['IDLE','RESEARCHING','EMBEDDING','VERIFYING','DRAFTING','REPORTING','COMPLETE']

function PipelineSteps({ currentState }) {
  const currentIdx = STEP_ORDER.indexOf(currentState)
  return (
    <div className="flex items-center justify-center gap-0">
      {PIPELINE_STEPS.map((step, i) => {
        const stepIdx = STEP_ORDER.indexOf(step.key)
        const done = currentIdx > stepIdx
        const active = currentIdx === stepIdx
        const isLast = i === PIPELINE_STEPS.length - 1
        return (
          <React.Fragment key={step.key}>
            <div className="flex flex-col items-center gap-1.5">
              <div className={`w-9 h-9 rounded-full border-2 flex items-center justify-center text-sm font-mono transition-all duration-500 ${
                done ? 'border-emerald-500 bg-emerald-900/30 text-emerald-400'
                : active ? 'border-violet-500 bg-violet-900/40 text-violet-300 pulse-ring'
                : 'border-[#1e1535] bg-[#0d0a1a] text-gray-600'
              }`}>
                {done ? '✓' : step.icon}
              </div>
              <span className={`text-[10px] font-mono tracking-wider ${
                active ? 'text-violet-400' : done ? 'text-emerald-500' : 'text-gray-600'
              }`}>{step.label}</span>
            </div>
            {!isLast && <div className={`w-10 h-px mb-5 transition-all duration-500 ${done ? 'bg-emerald-700' : 'bg-[#1e1535]'}`} />}
          </React.Fragment>
        )
      })}
    </div>
  )
}

function HowItWorks() {
  const steps = [
    { icon: '📝', title: 'Submit Your Topic', desc: 'Enter any research topic or paste your draft text. Zora accepts both.' },
    { icon: '🔍', title: 'Autonomous Research', desc: 'Zora searches ArXiv, academic databases, and the web — finding the top 5 verified sources.' },
    { icon: '🧠', title: 'Vector Memory', desc: 'All sources are embedded into a local vector database for semantic search and retrieval.' },
    { icon: '⚡', title: 'Claim Verification', desc: 'Each sentence in your draft is checked against real sources. Claims are tagged Verified, Partial, or Hallucinated.' },
    { icon: '✍️', title: 'Grounded Draft', desc: 'Zora generates or improves your draft with inline citations — every claim backed by a source.' },
    { icon: '📜', title: 'Research Receipt', desc: 'A tamper-evident PDF is generated with your Zora ID, Integrity Score, and full source map.' },
  ]
  return (
    <div className="mb-12">
      <div className="text-center mb-8">
        <h2 className="text-xl font-display font-bold text-white mb-2">How Zora Works</h2>
        <p className="text-sm text-gray-500 font-body">A 6-step multi-agent pipeline that turns raw topics into verified research</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {steps.map((s, i) => (
          <div key={i} className="p-4 rounded-xl border border-[#1e1535] bg-[#0d0a1a] hover:border-violet-800/50 transition-all group">
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-lg bg-[#1a0f30] border border-violet-900/50 flex items-center justify-center text-lg flex-shrink-0 group-hover:border-violet-600 transition-all">
                {s.icon}
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono text-violet-500">0{i+1}</span>
                  <h3 className="text-sm font-display font-semibold text-gray-200">{s.title}</h3>
                </div>
                <p className="text-xs text-gray-500 leading-relaxed">{s.desc}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function AgentCards() {
  const agents = [
    { name: 'Orchestrator', role: 'The Brain', desc: 'Finite State Machine that manages all agents and routes data between them.', color: 'violet' },
    { name: 'Researcher', role: 'The Librarian', desc: 'Searches ArXiv, web, and academic sources. Scrapes and extracts clean content.', color: 'blue' },
    { name: 'Verifier', role: 'The Editor', desc: 'Anti-hallucination engine. Checks every claim using cosine similarity + LLM critique.', color: 'amber' },
    { name: 'Citation Specialist', role: 'The Archivist', desc: 'Generates APA citations, improves drafts, and compiles the Research Receipt PDF.', color: 'emerald' },
  ]
  const colors = {
    violet: 'border-violet-900/50 text-violet-400 bg-violet-900/10',
    blue:   'border-blue-900/50 text-blue-400 bg-blue-900/10',
    amber:  'border-amber-900/50 text-amber-400 bg-amber-900/10',
    emerald:'border-emerald-900/50 text-emerald-400 bg-emerald-900/10',
  }
  return (
    <div className="mb-12">
      <div className="text-center mb-6">
        <h2 className="text-xl font-display font-bold text-white mb-2">Meet the Agents</h2>
        <p className="text-sm text-gray-500">4 specialized AI agents working in coordination</p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {agents.map((a, i) => (
          <div key={i} className={`p-4 rounded-xl border ${colors[a.color]} transition-all`}>
            <div className="text-xs font-mono mb-1 opacity-70">{a.role}</div>
            <div className="text-sm font-display font-bold text-white mb-2">{a.name}</div>
            <p className="text-xs text-gray-500 leading-relaxed">{a.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function ResultTabs({ result }) {
  const [tab, setTab] = useState('draft')
  const tabs = [
    { key: 'draft', label: '✍️ Final Draft' },
    { key: 'sources', label: `📚 Sources (${result.sources?.length || 0})` },
    { key: 'verify', label: `⚡ Verify (${result.verification_log?.length || 0})` },
    { key: 'receipt', label: '📜 Receipt' },
  ]
  return (
    <div className="space-y-4">
      <div className="flex gap-1 bg-[#0d0a1a] p-1 rounded-xl border border-[#1e1535]">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex-1 py-2 px-2 rounded-lg text-xs font-display font-medium transition-all ${
              tab === t.key ? 'bg-violet-900 text-violet-200 shadow-lg' : 'text-gray-500 hover:text-gray-300'
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'draft' && (
        <div className="space-y-3">
          <div className="p-5 rounded-xl border border-[#1e1535] bg-[#0d0a1a]">
            {(result.final_text || '').split('\n').map((para, i) =>
              para.trim() ? <p key={i} className="text-gray-300 leading-relaxed mb-3 text-sm">{para}</p> : <br key={i} />
            )}
          </div>
          {result.bibliography?.length > 0 && (
            <div className="p-4 rounded-xl border border-[#1e1535] bg-[#0a0716]">
              <h4 className="text-xs font-mono uppercase tracking-widest text-violet-500 mb-3">APA Bibliography</h4>
              {result.bibliography.map((cite, i) => (
                <p key={i} className="text-xs text-gray-500 font-mono leading-relaxed pl-4 -indent-4 mb-2">{cite}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'sources' && (
        <div className="grid gap-3">
          {(result.sources || []).map((s, i) => <SourceCard key={s.id} source={s} index={i} />)}
        </div>
      )}

      {tab === 'verify' && <VerificationLog chunks={result.verification_log || []} />}

      {tab === 'receipt' && (
        <div className="space-y-4">
          {result.receipt_url ? (
            <div className="p-6 rounded-xl border border-violet-900/50 bg-[#0d0a1a] text-center">
              <div className="text-4xl mb-3">📜</div>
              <h3 className="text-lg font-display font-semibold text-violet-300 mb-1">Research Receipt Ready</h3>
              <p className="text-sm text-gray-500 mb-4">Your tamper-evident Research Receipt PDF has been generated with your Zora ID.</p>
              <a href={result.receipt_url} target="_blank" rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-violet-700 hover:bg-violet-600 text-white rounded-xl text-sm font-display font-semibold transition-all glow-purple">
                ↓ Download Receipt PDF
              </a>
            </div>
          ) : (
            <div className="p-6 rounded-xl border border-[#1e1535] bg-[#0d0a1a] text-center">
              <p className="text-gray-500 text-sm">Check the <code className="text-violet-400">output/receipts/</code> folder for your receipt.</p>
            </div>
          )}
          {result.interaction_log?.length > 0 && (
            <div className="p-4 rounded-xl border border-[#1e1535] bg-[#0a0716]">
              <h4 className="text-xs font-mono uppercase tracking-widest text-violet-500 mb-3">Interaction Log — Proves Human Oversight</h4>
              {result.interaction_log.map((log, i) => (
                <div key={i} className="flex gap-3 text-xs font-mono p-2 rounded-lg bg-[#0d0a1a] border border-[#1e1535] mb-1">
                  <span className="text-violet-500 uppercase font-semibold flex-shrink-0">{log.role}</span>
                  <span className="text-gray-400">{log.content}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [topic, setTopic] = useState('')
  const [draft, setDraft] = useState('')
  const [showDraft, setShowDraft] = useState(false)
  const [showHowItWorks, setShowHowItWorks] = useState(false)
  const { state, logs, result, error, isRunning, runResearch, cancel } = useVera()

  const handleSubmit = () => {
    if (!topic.trim() || isRunning) return
    runResearch({ topic: topic.trim(), draft_text: draft.trim() || undefined })
  }

  const isComplete = state === 'COMPLETE'
  const hasResult = result && isComplete

  return (
    <div className="min-h-screen bg-[#06040f]" style={{ background: 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(124,58,237,0.1), transparent)' }}>
      {/* Grid bg */}
      <div className="fixed inset-0 pointer-events-none" style={{
        backgroundImage: 'linear-gradient(rgba(124,58,237,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(124,58,237,0.03) 1px,transparent 1px)',
        backgroundSize: '40px 40px',
      }} />

      <div className="relative max-w-4xl mx-auto px-4 py-10">

        {/* ===== HEADER ===== */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-[#0d0a1a] border border-violet-900/50 rounded-full px-4 py-1.5 mb-6 text-xs font-mono text-violet-400">
            <span className="w-1.5 h-1.5 bg-violet-500 rounded-full pulse-ring inline-block" />
            Multi-Agent Academic Research System · v1.0
          </div>

          <h1 className="text-6xl font-display font-bold tracking-tight mb-3 glow-text">
            <span className="text-white">ZORA</span>
            <span className="text-violet-500">.</span>
          </h1>

          <p className="text-gray-400 font-body text-lg font-light mb-2">
            The Integrity Agent — Verifiable Research with a Tamper-Evident Proof Trail
          </p>

          <p className="text-gray-600 font-body text-sm max-w-xl mx-auto leading-relaxed mb-6">
            Zora is an agentic research assistant that documents every step of the research process —
            from search queries and source retrieval to content verification and citation —
            generating an immutable <span className="text-violet-400">Research Receipt</span> that proves your work is fact-grounded.
          </p>

          <div className="flex justify-center flex-wrap gap-3 mb-6">
            {[
              { label: 'RAG Pipeline', color: 'text-violet-400 border-violet-900/50 bg-violet-900/10' },
              { label: 'Multi-Agent', color: 'text-blue-400 border-blue-900/50 bg-blue-900/10' },
              { label: 'Anti-Hallucination', color: 'text-amber-400 border-amber-900/50 bg-amber-900/10' },
              { label: 'APA Citations', color: 'text-emerald-400 border-emerald-900/50 bg-emerald-900/10' },
              { label: 'PDF Receipt', color: 'text-pink-400 border-pink-900/50 bg-pink-900/10' },
            ].map(tag => (
              <span key={tag.label} className={`text-xs font-mono px-3 py-1 rounded-full border ${tag.color}`}>
                {tag.label}
              </span>
            ))}
          </div>

          {/* Toggle how it works */}
          <button
            onClick={() => setShowHowItWorks(!showHowItWorks)}
            className="text-xs font-mono text-gray-500 hover:text-violet-400 transition-colors border border-[#1e1535] hover:border-violet-800 px-4 py-2 rounded-full"
          >
            {showHowItWorks ? '▲ Hide Details' : '▼ How does Zora work?'}
          </button>
        </div>

        {/* ===== HOW IT WORKS (collapsible) ===== */}
        {showHowItWorks && (
          <div className="mb-4">
            <HowItWorks />
            <AgentCards />
          </div>
        )}

        {/* ===== INPUT FORM ===== */}
        {!isRunning && !hasResult && (
          <div className="space-y-4 mb-8">
            <div className="p-6 rounded-2xl border border-[#1e1535] bg-[#0d0a1a]">
              <h3 className="text-sm font-display font-semibold text-gray-300 mb-4">
                🚀 Start Research
              </h3>

              <div className="space-y-4">
                <div className="relative">
                  <label className="text-xs font-mono text-gray-500 mb-2 block uppercase tracking-widest">Research Topic</label>
                  <textarea
                    value={topic}
                    onChange={e => setTopic(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && (e.metaKey || e.ctrlKey) && handleSubmit()}
                    placeholder="e.g. 'Impact of social media on teenage mental health'"
                    rows={3}
                    className="w-full px-4 py-3 bg-[#0a0716] border border-[#1e1535] rounded-xl text-gray-200 placeholder-gray-600 focus:outline-none focus:border-violet-600 font-body text-sm resize-none leading-relaxed animated-border"
                  />
                  <div className="absolute bottom-3 right-3 text-xs font-mono text-gray-700">⌘↵ to run</div>
                </div>

                <div>
                  <button
                    onClick={() => setShowDraft(!showDraft)}
                    className="flex items-center gap-2 text-xs font-mono text-gray-500 hover:text-violet-400 transition-colors mb-2"
                  >
                    <span className="text-violet-600">{showDraft ? '▾' : '▸'}</span>
                    {showDraft ? 'Hide draft' : 'Add a draft to verify'} (optional — for hallucination checking)
                  </button>

                  {showDraft && (
                    <textarea
                      value={draft}
                      onChange={e => setDraft(e.target.value)}
                      placeholder="Paste your draft here. Zora will verify each claim against real sources and highlight hallucinations with suggestions..."
                      rows={6}
                      className="w-full px-4 py-3 bg-[#0a0716] border border-[#1e1535] rounded-xl text-gray-300 placeholder-gray-600 focus:outline-none focus:border-violet-600 font-body text-sm resize-none leading-relaxed"
                    />
                  )}
                </div>

                <button
                  onClick={handleSubmit}
                  disabled={!topic.trim() || isRunning}
                  className="w-full py-4 bg-violet-700 hover:bg-violet-600 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl font-display font-semibold text-sm transition-all glow-purple"
                >
                  ⚡ Run Zora Pipeline
                </button>
              </div>
            </div>

            {/* Sample topics */}
            <div>
              <p className="text-xs font-mono text-gray-600 mb-2 uppercase tracking-widest">Try a sample topic:</p>
              <div className="flex flex-wrap gap-2">
                {[
                  'Effects of sleep deprivation on academic performance',
                  'AI in medical diagnosis',
                  'Climate change impact on biodiversity',
                  'Social media and teenage mental health',
                ].map(sample => (
                  <button
                    key={sample}
                    onClick={() => setTopic(sample)}
                    className="text-xs font-mono text-gray-500 hover:text-violet-400 border border-[#1e1535] hover:border-violet-800 px-3 py-1.5 rounded-lg transition-all"
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===== RUNNING ===== */}
        {isRunning && (
          <div className="space-y-6 mb-8">
            <div className="p-6 rounded-2xl border border-violet-900/30 bg-[#0d0a1a]">
              <p className="text-xs font-mono text-violet-400 uppercase tracking-widest mb-4 text-center">Pipeline Running</p>
              <PipelineSteps currentState={state} />
            </div>
            <LiveLog logs={logs} isRunning={isRunning} />
            <button onClick={cancel} className="w-full py-3 border border-red-900/50 text-red-500 hover:bg-red-900/10 rounded-xl text-sm font-mono transition-all">
              Cancel
            </button>
          </div>
        )}

        {/* ===== ERROR ===== */}
        {error && (
          <div className="mb-6 p-4 rounded-xl border border-red-900/50 bg-red-950/20 text-red-400 text-sm font-mono">
            ✗ {error}
            <button onClick={() => window.location.reload()} className="ml-4 underline hover:text-red-300">Reset</button>
          </div>
        )}

        {/* ===== RESULT ===== */}
        {hasResult && (
          <div className="space-y-6">
            {/* Score row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <IntegrityScore score={result.integrity_score || 0} />
              <div className="md:col-span-2 grid grid-cols-2 gap-3">
                {[
                  { label: 'Sources Found', value: result.sources?.length || 0, icon: '📚' },
                  { label: 'Claims Checked', value: result.verification_log?.length || 0, icon: '🔍' },
                  { label: 'Verified', value: result.verification_log?.filter(v => v.status === 'Verified').length || 0, icon: '✅' },
                  { label: 'Issues Found', value: result.verification_log?.filter(v => v.status === 'Hallucinated').length || 0, icon: '⚠️' },
                ].map(stat => (
                  <div key={stat.label} className="p-4 rounded-xl border border-[#1e1535] bg-[#0d0a1a]">
                    <div className="text-2xl mb-1">{stat.icon}</div>
                    <div className="text-2xl font-display font-bold text-white">{stat.value}</div>
                    <div className="text-xs text-gray-500 font-mono">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {result.queries?.length > 0 && (
              <div className="p-4 rounded-xl border border-[#1e1535] bg-[#0a0716]">
                <p className="text-xs font-mono uppercase tracking-widest text-violet-500 mb-2">Queries Executed</p>
                <div className="flex flex-wrap gap-2">
                  {result.queries.map((q, i) => (
                    <span key={i} className="text-xs font-mono bg-[#1a0f30] text-violet-400 border border-violet-900/50 px-2 py-1 rounded">{q}</span>
                  ))}
                </div>
              </div>
            )}

            <ResultTabs result={result} />

            <button onClick={() => window.location.reload()}
              className="w-full py-3 border border-[#1e1535] hover:border-violet-800 text-gray-400 hover:text-violet-400 rounded-xl text-sm font-mono transition-all">
              ← Start a new research session
            </button>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-16 text-center space-y-2">
          <p className="text-xs font-mono text-gray-700">
            ZORA · The Integrity Agent · Academic Research with a Tamper-Evident Proof Trail
          </p>
          <p className="text-xs font-mono text-gray-800">
            Built with FastAPI · LangGraph · ChromaDB · Gemini AI · React
          </p>
        </footer>
      </div>
    </div>
  )
}
