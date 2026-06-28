import { useState, useRef, useEffect, useCallback } from 'react'
import api from '../api/axios'
import useThemeStore from '../store/themeStore'
import useAuthStore from '../store/authStore'

// Suggestions réservées au personnel médical (médecin/secrétaire).
const STAFF_SUGGESTIONS = [
  { label: '🩺 Analyser symptômes', text: 'Analyser des symptômes' },
  { label: '👤 Nouveau Patient',    text: 'Ajouter un nouveau patient' },
  { label: '📅 Prochains RDV',     text: 'Planning de demain' },
  { label: '📊 Statistiques',      text: 'Statistiques du cabinet' },
]

// Suggestions pour le patient : uniquement ses propres données.
const PATIENT_SUGGESTIONS = [
  { label: '🩺 Analyser symptômes', text: 'Analyser mes symptômes' },
  { label: '📅 Mes prochains RDV',  text: 'Mes prochains rendez-vous' },
  { label: '💊 Mes ordonnances',    text: 'Mes ordonnances' },
  { label: '📋 Mes consultations',  text: 'Mes dernières consultations' },
]

export default function ChatbotWidget() {
  const { resolvedTheme } = useThemeStore()
  const dark = resolvedTheme === 'dark'
  const { user } = useAuthStore()
  const SUGGESTIONS = user?.role === 'patient' ? PATIENT_SUGGESTIONS : STAFF_SUGGESTIONS

  const [open, setOpen]       = useState(false)
  const [messages, setMessages] = useState([{
    role: 'bot',
    text: "Bonjour ! 👋 Je suis l'assistant **CuraMedical**. Comment puis-je vous assister aujourd'hui ?",
    time: new Date(),
  }])
  const [input, setInput]     = useState('')
  const [loading, setLoading] = useState(false)
  const [context, setContext] = useState(null)
  const endRef   = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    if (open) { setTimeout(scrollToBottom, 100); inputRef.current?.focus() }
  }, [messages, open, scrollToBottom])

  const sendMessage = async (text) => {
    const msg = (text?.trim() || input.trim())
    if (!msg) return
    setMessages(p => [...p, { role: 'user', text: msg, time: new Date() }])
    setInput('')
    setLoading(true)
    try {
      const payload = { message: msg }
      if (context) payload.context = context
      const { data } = await api.post('/api/chat/', payload)
      setContext(data.context || null)
      setMessages(p => [...p, { role: 'bot', text: data.response, time: new Date(), actions: data.actions || null }])
    } catch {
      setMessages(p => [...p, { role: 'bot', text: "Désolé, je rencontre une difficulté de connexion. Réessayez dans un instant. 🔄", time: new Date() }])
      setContext(null)
    } finally { setLoading(false) }
  }

  const cancelFlow = () => {
    setContext(null)
    setMessages(p => [...p, { role: 'bot', text: "❌ Opération annulée. Que puis-je faire pour vous ?", time: new Date() }])
  }

  const fmtTime = (d) => new Date(d).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })

  const renderText = (t) => {
    if (!t) return null
    return t.split(/(\*\*.*?\*\*|\n)/g).map((part, i) => {
      if (part === '\n') return <br key={i} />
      if (part.startsWith('**') && part.endsWith('**'))
        return <strong key={i} style={{ fontWeight: 700, color: dark ? '#f0f5fb' : '#0f172a' }}>{part.slice(2, -2)}</strong>
      return <span key={i}>{part}</span>
    })
  }

  /* ── Theme-derived style tokens ── */
  const t = {
    window:      dark ? '#1a2230' : '#ffffff',
    windowBorder:dark ? '#1d2630' : '#e2e8f0',
    msgArea:     dark ? '#0f1419' : '#f8fafc',
    botBubble:   dark ? '#1a2230' : '#ffffff',
    botBubbleBorder: dark ? '#253040' : '#e2e8f0',
    botText:     dark ? '#c8d4e0' : '#334155',
    botMeta:     dark ? '#546070' : '#94a3b8',
    userMeta:    'rgba(255,255,255,0.4)',
    suggestBar:  dark ? '#1a2230' : '#ffffff',
    suggestBarBorder: dark ? '#1d2630' : '#f1f5f9',
    suggestBtn:  dark ? '#0f1419' : '#f8fafc',
    suggestBtnBorder: dark ? '#253040' : '#e2e8f0',
    suggestText: dark ? '#a8b8c8' : '#475569',
    inputArea:   dark ? '#1a2230' : '#ffffff',
    inputAreaBorder: dark ? '#1d2630' : '#f1f5f9',
    inputBg:     dark ? '#0f1419' : 'rgba(248,250,252,0.5)',
    inputBorder: dark ? '#253040' : '#e2e8f0',
    inputText:   dark ? '#e2eaf2' : '#1e293b',
    inputPlaceholder: dark ? '#546070' : '#94a3b8',
    footerText:  dark ? '#3a4a5c' : '#cbd5e1',
    scrollThumb: dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.05)',
    actionBtn:   dark ? '#0f1419' : '#ffffff',
    actionBtnBorder: dark ? 'rgba(42,155,105,0.3)' : '#d1fae5',
    actionBtnText: dark ? '#4eb583' : '#059669',
    loadingBg:   dark ? '#1a2230' : '#ffffff',
    loadingBorder: dark ? '#253040' : '#e2e8f0',
  }

  return (
    <>
      {/* ── FAB ── */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-[9999] w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 active:scale-95"
          style={{ background: 'linear-gradient(135deg,#10b981,#059669)', boxShadow: '0 8px 32px rgba(16,185,129,0.35)', color: 'white' }}
          aria-label="Ouvrir le chatbot"
        >
          <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>neurology</span>
          <span className="absolute inset-0 rounded-2xl animate-ping pointer-events-none" style={{ background: 'rgba(16,185,129,0.2)' }} />
        </button>
      )}

      {/* ── Chat window ── */}
      {open && (
        <div
          className="fixed bottom-6 right-6 z-[9998] w-[440px] max-w-[calc(100vw-48px)] flex flex-col overflow-hidden"
          style={{
            height: 700, maxHeight: 'calc(100vh - 48px)',
            borderRadius: '2rem',
            background: t.window,
            border: `1px solid ${t.windowBorder}`,
            boxShadow: dark
              ? '0 32px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04)'
              : '0 32px 80px rgba(0,0,0,0.18)',
            animation: 'chatPopUp 0.4s cubic-bezier(0.16,1,0.3,1)',
          }}
        >
          {/* Header — toujours vert émeraude */}
          <div className="shrink-0 h-16 flex items-center px-5 relative overflow-hidden"
            style={{ background: 'linear-gradient(90deg,#064e3b,#065f46,#047857)' }}>
            <div className="absolute top-0 right-0 w-32 h-32 rounded-full -translate-y-1/2 translate-x-1/2"
              style={{ background: 'rgba(255,255,255,0.08)', filter: 'blur(24px)' }} />
            <div className="flex items-center gap-3 relative z-10 w-full">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white"
                style={{ background: 'rgba(255,255,255,0.15)', backdropFilter: 'blur(8px)' }}>
                <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>neurology</span>
              </div>
              <div className="flex-1">
                <h2 className="text-white font-black text-[15px] tracking-tight leading-none mb-1">CuraMedical AI</h2>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full animate-pulse"
                    style={{ background: '#6ee7b7', boxShadow: '0 0 8px rgba(110,231,183,0.8)' }} />
                  <p className="text-[9px] font-bold uppercase tracking-widest" style={{ color: '#a7f3d0' }}>
                    Assistant Intelligent
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                {context && (
                  <button onClick={cancelFlow}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-white transition-all"
                    style={{ background: 'rgba(0,0,0,0.15)', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <span className="material-symbols-outlined text-[17px]">block</span>
                  </button>
                )}
                <button onClick={() => setOpen(false)}
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-white transition-all"
                  style={{ background: 'rgba(0,0,0,0.15)', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <span className="material-symbols-outlined text-[17px]">close</span>
                </button>
              </div>
            </div>
          </div>

          {/* Messages area */}
          <div className="flex-1 overflow-y-auto px-5 py-6 space-y-5 chatbot-scroll"
            style={{ background: t.msgArea }}>
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                style={{ animation: 'fadeInMsg 0.3s ease' }}>
                <div
                  className="max-w-[85%] px-4 py-3 text-[13.5px] leading-relaxed"
                  style={{
                    background: msg.role === 'user'
                      ? 'linear-gradient(135deg,#1e293b,#0f172a)'
                      : t.botBubble,
                    color: msg.role === 'user' ? '#f0f5fb' : t.botText,
                    border: msg.role === 'user' ? 'none' : `1px solid ${t.botBubbleBorder}`,
                    borderRadius: msg.role === 'user' ? '1.25rem 1.25rem 0.25rem 1.25rem' : '1.25rem 1.25rem 1.25rem 0.25rem',
                    boxShadow: dark
                      ? '0 2px 8px rgba(0,0,0,0.3)'
                      : '0 2px 8px rgba(0,0,0,0.06)',
                  }}
                >
                  <div className="whitespace-pre-wrap">{renderText(msg.text)}</div>
                  <div className="mt-2 pt-1 flex justify-between items-center text-[10px] font-bold uppercase tracking-widest"
                    style={{ borderTop: `1px solid ${msg.role === 'user' ? 'rgba(255,255,255,0.08)' : (dark ? '#1d2630' : '#f1f5f9')}`, color: msg.role === 'user' ? t.userMeta : t.botMeta }}>
                    <span>{msg.role === 'user' ? 'Vous' : 'CuraMedical'}</span>
                    <span>{fmtTime(msg.time)}</span>
                  </div>
                </div>
                {msg.actions && (
                  <div className="flex flex-wrap gap-2 mt-3 ml-1">
                    {msg.actions.map((a, i) => (
                      <button key={i} onClick={() => sendMessage(a)}
                        className="text-[11px] px-3 py-1.5 rounded-xl font-bold transition-all"
                        style={{
                          background: t.actionBtn,
                          color: t.actionBtnText,
                          border: `1px solid ${t.actionBtnBorder}`,
                        }}
                        onMouseEnter={e => { e.currentTarget.style.background = '#10b981'; e.currentTarget.style.color = 'white' }}
                        onMouseLeave={e => { e.currentTarget.style.background = t.actionBtn; e.currentTarget.style.color = t.actionBtnText }}
                      >
                        {a}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex flex-col gap-2 items-start" style={{ animation: 'fadeInMsg 0.3s ease' }}>
                <div className="px-4 py-3 rounded-[1.25rem] rounded-tl-[0.25rem] flex gap-1 items-center"
                  style={{ background: t.loadingBg, border: `1px solid ${t.loadingBorder}` }}>
                  {[0, 0.2, 0.4].map((d, i) => (
                    <div key={i} className="w-1.5 h-1.5 rounded-full animate-bounce"
                      style={{ background: '#10b981', animationDelay: `${d}s` }} />
                  ))}
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest ml-1"
                  style={{ color: t.botMeta }}>Analyse…</span>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Suggestions */}
          {!loading && (
            <div className="shrink-0 px-5 py-3 flex gap-2 overflow-x-auto no-scrollbar"
              style={{ background: t.suggestBar, borderTop: `1px solid ${t.suggestBarBorder}` }}>
              {SUGGESTIONS.map((s, i) => (
                <button key={i} onClick={() => sendMessage(s.text)}
                  className="shrink-0 flex items-center gap-2 px-3 py-2 rounded-xl text-[11px] font-bold transition-all active:scale-95"
                  style={{
                    background: t.suggestBtn,
                    color: t.suggestText,
                    border: `1px solid ${t.suggestBtnBorder}`,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = dark ? 'rgba(42,155,105,0.12)' : '#ecfdf5'; e.currentTarget.style.color = '#059669'; e.currentTarget.style.borderColor = dark ? 'rgba(42,155,105,0.3)' : '#a7f3d0' }}
                  onMouseLeave={e => { e.currentTarget.style.background = t.suggestBtn; e.currentTarget.style.color = t.suggestText; e.currentTarget.style.borderColor = t.suggestBtnBorder }}
                >
                  {s.label}
                </button>
              ))}
            </div>
          )}

          {/* Input area */}
          <div className="shrink-0 p-4"
            style={{ background: t.inputArea, borderTop: `1px solid ${t.inputAreaBorder}` }}>
            <form onSubmit={e => { e.preventDefault(); if (input.trim() && !loading) sendMessage() }}
              className="flex items-center gap-3">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder={context ? `Étape ${context.step}/${context.total_steps}…` : "Une question pour l'Assistant ?"}
                  disabled={loading}
                  className="w-full rounded-2xl px-5 py-3 text-sm font-medium outline-none transition-all"
                  style={{
                    background: t.inputBg,
                    border: `1px solid ${t.inputBorder}`,
                    color: t.inputText,
                  }}
                  onFocus={e => { e.currentTarget.style.borderColor = '#10b981'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(16,185,129,0.12)' }}
                  onBlur={e => { e.currentTarget.style.borderColor = t.inputBorder; e.currentTarget.style.boxShadow = 'none' }}
                />
              </div>
              <button type="submit" disabled={!input.trim() || loading}
                className="w-12 h-12 rounded-2xl flex items-center justify-center transition-all hover:scale-105 active:scale-95 disabled:opacity-30"
                style={{ background: 'linear-gradient(135deg,#10b981,#059669)', boxShadow: '0 4px 14px rgba(16,185,129,0.3)', color: 'white' }}>
                <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
              </button>
            </form>
            <p className="text-[9px] text-center font-bold uppercase tracking-widest mt-3"
              style={{ color: t.footerText }}>
              CuraMedical v2.0 · IA Médicale Assistée
            </p>
          </div>
        </div>
      )}

      <style>{`
        @keyframes chatPopUp {
          from { opacity: 0; transform: translateY(32px) scale(0.96); }
          to   { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes fadeInMsg {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .chatbot-scroll::-webkit-scrollbar { width: 5px; }
        .chatbot-scroll::-webkit-scrollbar-track { background: transparent; }
        .chatbot-scroll::-webkit-scrollbar-thumb { background: rgba(128,147,168,0.2); border-radius: 10px; }
        .chatbot-scroll::-webkit-scrollbar-thumb:hover { background: rgba(128,147,168,0.35); }
      `}</style>
    </>
  )
}
