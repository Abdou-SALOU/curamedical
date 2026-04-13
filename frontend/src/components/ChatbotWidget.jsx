import { useState, useRef, useEffect, useCallback } from 'react'
import api from '../api/axios'

const SUGGESTIONS = [
  { label: '🩺 Analyser symptômes', text: 'Analyser mes symptômes', color: 'from-emerald-400 to-emerald-600' },
  { label: '👤 Nouveau Patient', text: 'Ajouter un nouveau patient', color: 'from-blue-400 to-indigo-600' },
  { label: '📅 Prochains RDV', text: 'Planning de demain', color: 'from-purple-400 to-fuchsia-600' },
  { label: '📊 Dashboard', text: 'Statistiques du cabinet', color: 'from-amber-400 to-orange-600' },
]

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: "Bonjour ! 👋 Je suis l'assistant **MedPredict**. Comment puis-je vous assister aujourd'hui ?",
      time: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [context, setContext] = useState(null)
  const endRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    if (open) {
      setTimeout(scrollToBottom, 100)
      inputRef.current?.focus()
    }
  }, [messages, open, scrollToBottom])

  const sendMessage = async (text) => {
    const messageText = text?.trim() || input.trim()
    if (!messageText) return

    const userMsg = { role: 'user', text: messageText, time: new Date() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const payload = { message: messageText }
      if (context) payload.context = context
      
      const { data } = await api.post('/api/chat/', payload)
      setContext(data.context || null)

      setMessages((prev) => [
        ...prev,
        { 
          role: 'bot', 
          text: data.response, 
          time: new Date(),
          actions: data.actions || null,
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text: "Désolé, je rencontre une petite difficulté de connexion. Réessayez dans un instant. 🔄",
          time: new Date(),
        },
      ])
      setContext(null)
    } finally {
      setLoading(false)
    }
  }

  const cancelFlow = () => {
    setContext(null)
    setMessages((prev) => [
      ...prev,
      { role: 'bot', text: "❌ Opération annulée. Revenons à nos moutons, que puis-je faire pour vous ?", time: new Date() },
    ])
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !loading) sendMessage()
  }

  const fmtTime = (d) => new Date(d).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })

  const renderText = (t) => {
    if (!t) return null
    return t.split(/(\*\*.*?\*\*|\n)/g).map((part, i) => {
      if (part === '\n') return <br key={i} />
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-bold text-slate-900">{part.slice(2, -2)}</strong>
      }
      return <span key={i}>{part}</span>
    })
  }

  return (
    <>
      {/* ── Floating Action Button ── */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-[9999] w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-700 text-white flex items-center justify-center transition-all duration-500 shadow-[0_8px_32px_rgba(16,185,129,0.3)] hover:scale-110 active:scale-95"
          aria-label="Open Chat"
        >
          <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>neurology</span>
          <span className="absolute inset-0 rounded-2xl animate-ping bg-emerald-400/20 pointer-events-none" />
        </button>
      )}

      {/* ── Chat Window ── */}
      {open && (
        <div
          className="fixed bottom-6 right-6 z-[9998] w-[440px] max-w-[calc(100vw-48px)] h-[700px] max-h-[calc(100vh-48px)] flex flex-col rounded-[2.5rem] overflow-hidden bg-white shadow-[0_32px_128px_rgba(0,0,0,0.18)] border border-slate-100"
          style={{ animation: 'chatPopUp 0.5s cubic-bezier(0.16, 1, 0.3, 1)' }}
        >
          {/* Header */}
          <div className="shrink-0 h-16 bg-gradient-to-r from-emerald-700 via-emerald-600 to-teal-700 flex items-center px-5 relative overflow-hidden">
             {/* Decorative backgrounds */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
            
            <div className="flex items-center gap-3 relative z-10 w-full">
              <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center text-white shadow-inner">
                <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>neurology</span>
              </div>
              <div className="flex-1">
                <h2 className="text-white font-black text-[15px] tracking-tight leading-none mb-1">MedPredict AI</h2>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-200 animate-pulse shadow-[0_0_8px_rgba(167,243,208,0.8)]" />
                  <p className="text-[9px] font-bold text-emerald-50 uppercase tracking-widest leading-none">Assistant Intelligent</p>
                </div>
              </div>
              
              <div className="flex items-center gap-1.5">
                {context && (
                  <button onClick={cancelFlow} className="w-8 h-8 rounded-lg bg-black/10 hover:bg-black/20 text-white transition-all flex items-center justify-center border border-white/10">
                    <span className="material-symbols-outlined text-[17px]">block</span>
                  </button>
                )}
                <button onClick={() => setOpen(false)} className="w-8 h-8 rounded-lg bg-black/10 hover:bg-black/20 text-white transition-all flex items-center justify-center border border-white/10">
                  <span className="material-symbols-outlined text-[17px]">close</span>
                </button>
              </div>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-6 py-8 space-y-8 soft-scrollbar bg-[#F8FAFC]">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} animate-fadeIn`}>
                <div
                  className={`max-w-[85%] px-5 py-4 text-[14px] leading-relaxed shadow-sm transition-all ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-br from-slate-800 to-slate-900 text-white rounded-[1.5rem] rounded-tr-none'
                      : 'bg-white border border-slate-100 text-slate-700 rounded-[1.5rem] rounded-tl-none shadow-slate-200/50'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{renderText(msg.text)}</div>
                  <div className={`mt-3 pt-2 flex justify-between items-center text-[10px] font-bold uppercase tracking-widest ${msg.role === 'user' ? 'text-white/40' : 'text-slate-400'}`}>
                    <span>{msg.role === 'user' ? 'Vous' : 'MedPredict'}</span>
                    <span>{fmtTime(msg.time)}</span>
                  </div>
                </div>
                {msg.actions && (
                  <div className="flex flex-wrap gap-2 mt-4 ml-1">
                    {msg.actions.map((a, i) => (
                      <button 
                        key={i} 
                        onClick={() => sendMessage(a)} 
                        className="text-[11px] px-4 py-2 rounded-xl bg-white text-emerald-600 hover:bg-emerald-500 hover:text-white font-bold transition-all border border-emerald-100 shadow-sm"
                      >
                        {a}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {loading && (
              <div className="flex flex-col gap-2 items-start animate-fadeIn">
                <div className="bg-white border border-slate-100 rounded-2xl rounded-tl-none px-5 py-4 flex gap-2 items-center shadow-sm shadow-slate-200/50">
                   <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce" />
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:0.2s]" />
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:0.4s]" />
                   </div>
                </div>
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Analyse intelligente...</span>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Quick Suggestions - Horizontal scrollable list above input */}
          {!loading && (
            <div className="shrink-0 px-6 py-4 bg-white border-t border-slate-100 flex gap-2 overflow-x-auto no-scrollbar">
              {SUGGESTIONS.map((s, i) => (
                <button 
                  key={i} 
                  onClick={() => sendMessage(s.text)} 
                  className="shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-slate-50 text-slate-600 hover:bg-emerald-50 hover:text-emerald-700 font-bold border border-slate-100 hover:border-emerald-100 transition-all active:scale-95 text-[11px]"
                >
                  {s.label}
                </button>
              ))}
            </div>
          )}

          {/* Input Area */}
          <div className="shrink-0 p-6 bg-white border-t border-slate-100">
            <form onSubmit={handleSubmit} className="flex items-center gap-3">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={context ? `Étape ${context.step}/${context.total_steps}...` : "Une question pour l'Assistant ?"}
                  disabled={loading}
                  className="w-full bg-slate-50/50 rounded-2xl px-6 py-4 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-emerald-500/10 border border-slate-100 focus:border-emerald-400 transition-all font-medium"
                />
              </div>
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 text-white flex items-center justify-center shadow-lg shadow-emerald-500/20 hover:scale-105 active:scale-95 transition-all disabled:opacity-20 disabled:grayscale"
              >
                <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
              </button>
            </form>
            <p className="text-[9px] text-center text-slate-400 font-bold uppercase tracking-widest mt-4 opacity-50">
               MedPredict v2.0 • IA Médicale Assistée
            </p>
          </div>
        </div>
      )}

      <style>{`
        @keyframes chatPopUp {
          from { opacity: 0; transform: translateY(40px) scale(0.95); filter: blur(15px); }
          to   { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .soft-scrollbar::-webkit-scrollbar { width: 5px; }
        .soft-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .soft-scrollbar::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.05); border-radius: 10px; }
        .soft-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.1); }
      `}</style>
    </>
  )
}
