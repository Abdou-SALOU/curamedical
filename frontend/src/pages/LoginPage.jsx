import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const FEATURES = [
  { icon: 'stethoscope',     title: 'Suivi clinique complet',   desc: 'Consultations, ordonnances et historiques patients centralisés.' },
  { icon: 'neurology',       title: 'Assistant IA intégré',     desc: 'Aide au diagnostic par analyse contextuelle des symptômes.' },
  { icon: 'event_available', title: 'Gestion des rendez-vous',  desc: 'Agenda médical intelligent avec notifications en temps réel.' },
]

export default function LoginPage() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPwd, setShowPwd] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(form.username, form.password)
      navigate('/')
    } catch {
      setError('Identifiants incorrects. Veuillez réessayer.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex overflow-hidden bg-slate-950">

      {/* ── LEFT: Marketing panel ── */}
      <div className="relative hidden lg:flex flex-col justify-between w-[52%] p-14 overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_-10%_40%,rgba(16,185,129,0.22),transparent_55%),radial-gradient(ellipse_60%_50%_at_110%_70%,rgba(99,102,241,0.16),transparent_55%),linear-gradient(180deg,#030c18_0%,#060f1e_100%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:48px_48px]" />
        <div className="absolute -left-20 top-1/3 w-72 h-72 rounded-full bg-emerald-500/15 blur-3xl" />
        <div className="absolute right-0 bottom-1/4 w-56 h-56 rounded-full bg-indigo-500/12 blur-3xl" />

        {/* Logo */}
        <div className="relative z-10 flex items-center gap-3">
          <div className="w-10 h-10 rounded-[12px] bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/30">
            <span className="material-symbols-outlined text-white text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>biotech</span>
          </div>
          <span className="text-white font-black text-lg tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>MedPredict</span>
        </div>

        {/* Hero copy */}
        <div className="relative z-10 space-y-8 max-w-[440px]">
          <div className="space-y-5">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-emerald-400/20 bg-emerald-400/8 text-emerald-300 text-xs font-bold uppercase tracking-widest">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Plateforme médicale
            </div>
            <h1 className="text-[52px] font-black leading-[0.92] tracking-tight text-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Pilotez votre cabinet avec précision.
            </h1>
            <p className="text-slate-400 text-base leading-relaxed">
              MedPredict unifie la coordination administrative, le suivi clinique
              et l&apos;aide IA dans un flux de travail fluide et sécurisé.
            </p>
          </div>

          <div className="space-y-3">
            {FEATURES.map(f => (
              <div key={f.title} className="flex items-start gap-4 p-4 rounded-2xl border border-white/6 bg-white/[0.04] backdrop-blur-sm">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400/20 to-teal-400/20 border border-emerald-400/20 flex items-center justify-center shrink-0 text-emerald-300">
                  <span className="material-symbols-outlined text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>{f.icon}</span>
                </div>
                <div>
                  <p className="text-white text-sm font-bold">{f.title}</p>
                  <p className="text-slate-500 text-xs mt-0.5 leading-relaxed">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <p className="relative z-10 text-slate-700 text-[11px] font-semibold uppercase tracking-widest">
          MedPredict © 2026 · Environnement sécurisé
        </p>
      </div>

      {/* ── RIGHT: Login form ── */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-slate-900">
        <div className="w-full max-w-[400px]">

          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-3 justify-center mb-10">
            <div className="w-10 h-10 rounded-[12px] bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>biotech</span>
            </div>
            <span className="text-white font-black text-lg" style={{ fontFamily: 'Manrope, sans-serif' }}>MedPredict</span>
          </div>

          {/* Heading */}
          <div className="mb-8">
            <h2 className="text-[32px] font-black text-white leading-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Connexion
            </h2>
            <p className="text-slate-500 text-sm mt-2">Accédez à votre espace professionnel sécurisé.</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">Identifiant</label>
              <div className="relative group">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-600 group-focus-within:text-emerald-400 transition-colors text-[20px] pointer-events-none">
                  badge
                </span>
                <input
                  type="text"
                  value={form.username}
                  onChange={e => setForm({ ...form, username: e.target.value })}
                  className="w-full pl-12 pr-4 py-3.5 rounded-2xl border border-white/8 bg-white/5 text-white placeholder:text-slate-600 text-sm focus:outline-none focus:border-emerald-400/50 focus:ring-2 focus:ring-emerald-400/15 transition-all"
                  placeholder="Nom d'utilisateur"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500">Mot de passe</label>
              <div className="relative group">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-600 group-focus-within:text-emerald-400 transition-colors text-[20px] pointer-events-none">
                  lock
                </span>
                <input
                  type={showPwd ? 'text' : 'password'}
                  value={form.password}
                  onChange={e => setForm({ ...form, password: e.target.value })}
                  className="w-full pl-12 pr-12 py-3.5 rounded-2xl border border-white/8 bg-white/5 text-white placeholder:text-slate-600 text-sm focus:outline-none focus:border-emerald-400/50 focus:ring-2 focus:ring-emerald-400/15 transition-all"
                  placeholder="••••••••"
                  required
                />
                <button type="button" onClick={() => setShowPwd(!showPwd)} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-300 transition-colors">
                  <span className="material-symbols-outlined text-[20px]">{showPwd ? 'visibility_off' : 'visibility'}</span>
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm">
                <span className="material-symbols-outlined text-[18px]">error</span>
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3.5 rounded-2xl font-bold text-sm text-slate-950 bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 shadow-[0_8px_24px_rgba(16,185,129,0.3)] hover:shadow-[0_12px_32px_rgba(16,185,129,0.45)] transition-all duration-200 hover:-translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed disabled:translate-y-0"
            >
              {loading
                ? <span className="w-5 h-5 rounded-full border-2 border-slate-950/20 border-t-slate-950 animate-spin" />
                : <><span className="material-symbols-outlined text-[18px]">login</span> Accéder à la plateforme</>
              }
            </button>
          </form>

          {/* Footer note */}
          <p className="text-center text-xs text-slate-700 mt-8">
            Accès réservé aux professionnels autorisés du cabinet.
          </p>
        </div>
      </div>
    </div>
  )
}
