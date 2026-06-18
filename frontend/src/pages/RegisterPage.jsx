import { useState, useEffect, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  ArrowRight, ArrowLeft, CheckCircle2, ShieldCheck,
  Mail, Phone, CreditCard, CalendarDays, User, Check,
  LockKeyhole, Eye, EyeOff, Activity,
} from 'lucide-react'
import api from '../api/axios'

const STEPS = [
  { id: 1, label: 'Identifiants',      desc: 'Nom, prénom et accès', icon: User },
  { id: 2, label: 'Contact',           desc: 'Email et téléphone',   icon: Mail },
  { id: 3, label: 'Données médicales', desc: 'CIN et profil santé',  icon: ShieldCheck },
]

/* ── Animated entrance ── */
function useReveal() {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      entries => entries.forEach(e => { if (e.isIntersecting) el.classList.add('in') }),
      { threshold: 0.05 },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [])
  return ref
}

function Fade({ children, delay = 0 }) {
  const ref = useReveal()
  return (
    <div ref={ref} className="reveal" style={{ transitionDelay: `${delay * 0.08}s` }}>
      {children}
    </div>
  )
}

/* ── BrandMark ── */
function BrandMark({ size = 38 }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: size * 0.275, flexShrink: 0,
      background: 'linear-gradient(140deg, #4eb583, #1d7f54)',
      display: 'grid', placeItems: 'center', color: 'white',
      boxShadow: '0 8px 30px rgba(42,155,105,0.4), inset 0 1px 0 rgba(255,255,255,0.25)',
    }}>
      <svg width={size * 0.55} height={size * 0.55} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2 4 6v6c0 5 3.5 9 8 10 4.5-1 8-5 8-10V6l-8-4Z" />
        <path d="M9 11h6M12 8v6" />
      </svg>
    </div>
  )
}

/* ── Mini dashboard preview ── */
function DashPreview() {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.035)',
      border: '1px solid rgba(255,255,255,0.09)',
      borderRadius: 18, overflow: 'hidden',
      backdropFilter: 'blur(20px)',
      boxShadow: '0 32px 80px rgba(0,0,0,0.5)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '12px 14px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        {['#d4543f', '#c98b1e', '#4eb583'].map((c, i) => (
          <span key={i} style={{ width: 9, height: 9, borderRadius: '50%', background: c, display: 'block' }} />
        ))}
        <span style={{ marginLeft: 'auto', fontSize: 10, color: '#6b7787', fontFamily: 'monospace' }}>
          cura.app / dashboard
        </span>
      </div>
      <div style={{ padding: 14, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        <MiniCard eyebrow="Consultations" value="324" delta="↑ +12.4%" />
        <MiniCard eyebrow="Adoption IA" value="64%" delta="↑ +8.1%">
          <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, marginTop: 10, overflow: 'hidden' }}>
            <div style={{ width: '64%', height: '100%', background: 'linear-gradient(90deg, #4eb583, #2a9b69)' }} />
          </div>
        </MiniCard>
        <div style={{ gridColumn: '1 / -1', background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, padding: '12px 14px' }}>
          <div style={{ fontSize: 9, textTransform: 'uppercase', letterSpacing: '0.14em', color: '#6b7787', fontWeight: 600, marginBottom: 10 }}>
            Rendez-vous · Aujourd'hui
          </div>
          {[
            { t: '08:30', p: 'K. Bensalem', s: 'Confirmé' },
            { t: '09:15', p: 'A. Tazi',     s: 'Téléconsult.' },
          ].map((r, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11, padding: '6px 0', borderBottom: i === 0 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
              <span style={{ fontFamily: 'monospace', color: '#98a3b1' }}>{r.t}</span>
              <span style={{ color: 'white', fontWeight: 500 }}>{r.p}</span>
              <span style={{ fontSize: 10, color: '#4eb583', fontWeight: 600 }}>{r.s}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function MiniCard({ eyebrow, value, delta, children }) {
  return (
    <div style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, padding: '12px 14px' }}>
      <div style={{ fontSize: 9, textTransform: 'uppercase', letterSpacing: '0.14em', color: '#6b7787', fontWeight: 600 }}>{eyebrow}</div>
      <div style={{ fontSize: 20, fontWeight: 700, fontFamily: 'monospace', color: 'white', marginTop: 6, letterSpacing: '-0.02em' }}>{value}</div>
      <div style={{ fontSize: 10, color: '#4eb583', fontWeight: 600, marginTop: 2 }}>{delta}</div>
      {children}
    </div>
  )
}

/* ── Field — defined OUTSIDE RegisterPage to keep stable identity across renders ── */
function Field({ label, icon: Icon, rightSlot, focused, onFocus, onBlur, inputStyle, ...inputProps }) {
  const active = focused === inputProps.name
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <label style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase', color: '#6b7787' }}>
        {label}
      </label>
      <div style={{ position: 'relative' }}>
        <div style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', zIndex: 1 }}>
          <Icon size={16} style={{ color: active ? '#4eb583' : '#4a5564', transition: 'color .15s' }} />
        </div>
        <input
          {...inputProps}
          onFocus={onFocus}
          onBlur={onBlur}
          style={{
            width: '100%', boxSizing: 'border-box',
            paddingLeft: 44,
            paddingRight: rightSlot ? 44 : 16,
            paddingTop: 13, paddingBottom: 13,
            background: active ? 'rgba(78,181,131,0.05)' : 'rgba(255,255,255,0.04)',
            border: active ? '1px solid #4eb583' : '1px solid rgba(255,255,255,0.1)',
            borderRadius: 12,
            color: 'white', fontSize: 14,
            outline: 'none', transition: 'all .18s',
            fontFamily: 'Inter, sans-serif',
            boxShadow: active ? '0 0 0 3px rgba(78,181,131,0.12)' : 'none',
            ...inputStyle,
          }}
          className="reg-input"
        />
        {rightSlot && (
          <div style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', zIndex: 1 }}>
            {rightSlot}
          </div>
        )}
      </div>
    </div>
  )
}

/* ── Navigation buttons ── */
function NavBtn({ canNext, onNext, onBack, isFirst }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: isFirst ? '1fr' : '1fr 2.5fr', gap: 10, marginTop: 4 }}>
      {!isFirst && <BackBtn onBack={onBack} />}
      <button
        type="button" onClick={onNext} disabled={!canNext}
        style={{
          padding: '13px 16px', borderRadius: 12, border: 0,
          background: 'linear-gradient(180deg, #4eb583, #1d7f54)',
          color: 'white', fontSize: 14, fontWeight: 600,
          cursor: canNext ? 'pointer' : 'not-allowed',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
          boxShadow: '0 12px 30px -8px rgba(42,155,105,0.5), inset 0 1px 0 rgba(255,255,255,0.2)',
          transition: 'transform .15s, box-shadow .2s, opacity .15s',
          opacity: canNext ? 1 : 0.45,
          fontFamily: 'Inter, sans-serif',
        }}
        onMouseEnter={e => { if (canNext) { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 16px 36px -8px rgba(42,155,105,0.6), inset 0 1px 0 rgba(255,255,255,0.2)' } }}
        onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '0 12px 30px -8px rgba(42,155,105,0.5), inset 0 1px 0 rgba(255,255,255,0.2)' }}
      >
        Continuer <ArrowRight size={17} />
      </button>
    </div>
  )
}

function BackBtn({ onBack }) {
  return (
    <button
      type="button" onClick={onBack}
      style={{
        padding: '13px', borderRadius: 12,
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(255,255,255,0.09)',
        color: '#6b7787', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        transition: 'background .15s, color .15s',
      }}
      onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.08)'; e.currentTarget.style.color = 'white' }}
      onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; e.currentTarget.style.color = '#6b7787' }}
    >
      <ArrowLeft size={16} />
    </button>
  )
}

/* ════════════════════════════════════════════
    MAIN COMPONENT
════════════════════════════════════════════ */
export default function RegisterPage() {
  const navigate = useNavigate()

  const [step, setStep]               = useState(1)
  const [form, setForm]               = useState({
    username: '', password: '', password_confirm: '', email: '',
    first_name: '', last_name: '',
    cin: '', date_naissance: '',
    sexe: 'M', telephone: '',
  })
  const [error, setError]             = useState('')
  const [loading, setLoading]         = useState(false)
  const [focused, setFocused]         = useState('')
  const [showPassword, setShowPassword]   = useState(false)
  const [showPassword2, setShowPassword2] = useState(false)

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }))

  const canNext = () => {
    if (step === 1) return form.first_name && form.last_name && form.username && form.password && form.password_confirm && form.password === form.password_confirm
    if (step === 2) return form.email && form.telephone
    return true
  }

  const next = () => { if (canNext()) { setError(''); setStep(s => s + 1) } }
  const back = () => { setError(''); setStep(s => s - 1) }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.post('/api/users/register/', form)
      navigate('/login', { state: { message: 'Inscription réussie ! Vous pouvez maintenant vous connecter.' } })
    } catch (err) {
      const data = err.response?.data
      if (data && typeof data === 'object') {
        const msg = data.detail
          || data.message
          || data.non_field_errors?.[0]
          || data.username?.[0]
          || data.email?.[0]
          || data.telephone?.[0]
          || data.cin?.[0]
          || data.date_naissance?.[0]
          || data.sexe?.[0]
          || data.password?.[0]
          || Object.values(data).flat()[0]
          || 'Une erreur est survenue.'
        setError(msg)
      } else {
        setError('Une erreur est survenue.')
      }
    } finally {
      setLoading(false)
    }
  }

  const progressPct = step === 1 ? '33%' : step === 2 ? '66%' : '100%'

  /* Shorthand to build Field props with shared focused state */
  const fp = (name) => ({
    name,
    focused,
    onFocus: () => setFocused(name),
    onBlur:  () => setFocused(''),
  })

  return (
    <>
      <style>{`
        .reg-input::placeholder { color: #3d4b58; }
        .reg-input[type="date"] { color-scheme: dark; }
        .reg-input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(0.5); cursor: pointer; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes regFadeUp {
          from { opacity: 0; transform: translateY(14px); }
          to   { opacity: 1; transform: none; }
        }
        .reg-animate { animation: regFadeUp .4s cubic-bezier(.2,.7,.2,1) both; }
        @keyframes pulse {
          0%,100% { box-shadow: 0 0 0 4px rgba(78,181,131,0.18); }
          50%      { box-shadow: 0 0 0 8px rgba(78,181,131,0.06); }
        }
        @media (max-width: 900px) { .reg-left-panel { display: none !important; } }
        @media (min-width: 901px) { .reg-mobile-header { display: none !important; } }
      `}</style>

      <div style={{ minHeight: '100vh', display: 'flex', background: '#06090d', color: 'white', fontFamily: 'Inter, sans-serif', position: 'relative' }}>

        {/* ── Mesh background ── */}
        <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0 }}>
          <div style={{
            position: 'absolute', inset: '-10%',
            background: `
              radial-gradient(900px 700px at 18% 22%, rgba(42,155,105,0.28), transparent 60%),
              radial-gradient(800px 600px at 90% 80%, rgba(65,120,214,0.14), transparent 60%),
              radial-gradient(500px 400px at 50% 50%, rgba(78,181,131,0.14), transparent 60%)`,
            filter: 'blur(30px)',
          }} />
          <div style={{
            position: 'absolute', inset: 0,
            backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.045) 1px, transparent 0)',
            backgroundSize: '28px 28px',
          }} />
        </div>

        {/* ════ LEFT PANEL ════ */}
        <aside className="reg-left-panel" style={{
          position: 'relative', zIndex: 1,
          width: 480, flexShrink: 0,
          display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
          padding: '44px 48px',
          borderRight: '1px solid rgba(255,255,255,0.06)',
          background: 'rgba(0,0,0,0.25)',
          backdropFilter: 'blur(16px)',
        }}>
          <div>
            <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: 12, textDecoration: 'none', marginBottom: 52 }}>
              <BrandMark size={40} />
              <div>
                <div style={{ fontSize: 16, fontWeight: 700, color: 'white' }}>CuraMedical</div>
                <div style={{ fontSize: 9, color: '#98a3b1', textTransform: 'uppercase', letterSpacing: '0.16em', marginTop: 1 }}>
                  Système médical IA
                </div>
              </div>
            </Link>

            <Fade>
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                padding: '6px 14px', borderRadius: 999,
                border: '1px solid rgba(78,181,131,0.3)',
                background: 'rgba(78,181,131,0.08)',
                color: '#87d1a8', fontSize: 11, fontWeight: 600,
                letterSpacing: '0.1em', textTransform: 'uppercase',
                fontFamily: 'monospace', marginBottom: 20,
              }}>
                <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#4eb583', display: 'inline-block', animation: 'pulse 1.6s ease-in-out infinite' }} />
                Inscription gratuite
              </div>
            </Fade>

            <Fade delay={1}>
              <h1 style={{ fontSize: 'clamp(30px, 3.2vw, 46px)', fontWeight: 700, lineHeight: 1.05, letterSpacing: '-0.04em', margin: '0 0 14px', color: 'white', fontFamily: 'Manrope, sans-serif' }}>
                Créez votre<br />
                <span style={{ background: 'linear-gradient(120deg, #b8e5cb, #4eb583 60%, #2a9b69)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }}>
                  espace patient.
                </span>
              </h1>
            </Fade>

            <Fade delay={2}>
              <p style={{ fontSize: 14, color: '#98a3b1', lineHeight: 1.65, maxWidth: 360, margin: '0 0 32px' }}>
                Rejoignez CuraMedical pour accéder à vos rendez-vous, ordonnances et à l'assistant IA de diagnostic.
              </p>
            </Fade>

            <Fade delay={3}>
              <DashPreview />
            </Fade>
          </div>

          {/* Step list + security */}
          <div style={{ marginTop: 36 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {STEPS.map(s => {
                const done = step > s.id
                const active = step === s.id
                const Icon = s.icon
                return (
                  <div key={s.id} style={{
                    display: 'flex', alignItems: 'center', gap: 14,
                    padding: '10px 14px', borderRadius: 14,
                    background: active ? 'rgba(78,181,131,0.08)' : 'transparent',
                    border: active ? '1px solid rgba(78,181,131,0.2)' : '1px solid rgba(255,255,255,0.04)',
                    opacity: !active && !done ? 0.4 : 1,
                    transition: 'all .3s',
                  }}>
                    <div style={{
                      width: 34, height: 34, borderRadius: 10, flexShrink: 0,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: done ? 'linear-gradient(135deg, #4eb583, #2a9b69)' : active ? 'rgba(78,181,131,0.15)' : 'rgba(255,255,255,0.05)',
                      border: done ? 'none' : active ? '1.5px solid rgba(78,181,131,0.35)' : '1.5px solid rgba(255,255,255,0.08)',
                      boxShadow: done ? '0 4px 14px rgba(42,155,105,0.35)' : 'none',
                    }}>
                      {done ? <Check size={15} color="white" strokeWidth={3} /> : <Icon size={15} color={active ? '#4eb583' : '#4a5564'} />}
                    </div>
                    <div>
                      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#4a5564', marginBottom: 1 }}>Étape {s.id}</div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: active ? '#4eb583' : done ? '#c8d4e0' : '#6b7787' }}>{s.label}</div>
                    </div>
                  </div>
                )
              })}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 16, padding: '12px 14px', borderRadius: 12, background: 'rgba(78,181,131,0.05)', border: '1px solid rgba(78,181,131,0.14)', fontSize: 11, color: '#6b7787' }}>
              <ShieldCheck size={15} color="#4eb583" style={{ flexShrink: 0 }} />
              <span>TLS 1.3 · AES-256 · Conformité RGPD</span>
            </div>
          </div>
        </aside>

        {/* ════ RIGHT PANEL — form ════ */}
        <main style={{
          flex: 1, position: 'relative', zIndex: 1,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: '48px 32px', overflowY: 'auto',
        }}>
          <div style={{ position: 'absolute', top: -80, right: -80, width: 400, height: 400, borderRadius: '50%', pointerEvents: 'none', background: 'radial-gradient(circle, rgba(78,181,131,0.07) 0%, transparent 70%)' }} />

          <div style={{ width: '100%', maxWidth: 460, position: 'relative' }} className="reg-animate">

            {/* Mobile logo */}
            <div className="reg-mobile-header" style={{ display: 'flex', alignItems: 'center', marginBottom: 32 }}>
              <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
                <BrandMark size={34} />
                <span style={{ fontSize: 15, fontWeight: 700, color: 'white', fontFamily: 'Manrope, sans-serif' }}>CuraMedical</span>
              </Link>
            </div>

            {/* Step header */}
            <div style={{ marginBottom: 22 }}>
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: 6,
                padding: '4px 12px', borderRadius: 999,
                background: 'rgba(78,181,131,0.10)',
                border: '1px solid rgba(78,181,131,0.22)',
                color: '#4eb583', fontSize: 10, fontWeight: 700,
                letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 10,
              }}>
                Étape {step} / {STEPS.length}
              </div>
              <h2 style={{ fontSize: 26, fontWeight: 700, margin: 0, color: 'white', letterSpacing: '-0.03em', fontFamily: 'Manrope, sans-serif' }}>
                {STEPS[step - 1].label}
              </h2>
              <p style={{ fontSize: 13, color: '#98a3b1', marginTop: 4, marginBottom: 0 }}>
                {STEPS[step - 1].desc}
              </p>
            </div>

            {/* Progress bar */}
            <div style={{ height: 3, borderRadius: 999, marginBottom: 26, background: 'rgba(255,255,255,0.07)', overflow: 'hidden' }}>
              <div style={{
                height: '100%', borderRadius: 999, width: progressPct,
                background: 'linear-gradient(90deg, #4eb583, #2a9b69)',
                boxShadow: '0 0 10px rgba(78,181,131,0.5)',
                transition: 'width .5s cubic-bezier(.4,0,.2,1)',
              }} />
            </div>

            {/* Form card */}
            <div style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 20, padding: '28px 28px 24px',
              backdropFilter: 'blur(24px)',
              boxShadow: '0 8px 40px rgba(0,0,0,0.45)',
            }}>

              {/* ── STEP 1 ── */}
              {step === 1 && (
                <div key="s1" className="reg-animate" style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                    <Field label="Prénom *" icon={User} {...fp('first_name')}
                      value={form.first_name} onChange={e => set('first_name', e.target.value)}
                      placeholder="Jean" required autoComplete="given-name" />
                    <Field label="Nom *" icon={User} {...fp('last_name')}
                      value={form.last_name} onChange={e => set('last_name', e.target.value)}
                      placeholder="Dupont" required autoComplete="family-name" />
                  </div>
                  <Field label="Nom d'utilisateur *" icon={User} {...fp('username')}
                    value={form.username} onChange={e => set('username', e.target.value)}
                    placeholder="jean.dupont" required autoComplete="username" />
                  <Field
                    label="Mot de passe *" icon={LockKeyhole} {...fp('password')}
                    type={showPassword ? 'text' : 'password'}
                    value={form.password} onChange={e => set('password', e.target.value)}
                    placeholder="••••••••" required autoComplete="new-password"
                    rightSlot={
                      <button type="button" onClick={() => setShowPassword(v => !v)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#4a5564', padding: 0, display: 'flex', alignItems: 'center' }}>
                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    }
                  />
                  <div>
                    <Field
                      label="Confirmer le mot de passe *" icon={LockKeyhole} {...fp('password_confirm')}
                      type={showPassword2 ? 'text' : 'password'}
                      value={form.password_confirm} onChange={e => set('password_confirm', e.target.value)}
                      placeholder="••••••••" required autoComplete="new-password"
                      rightSlot={
                        <button type="button" onClick={() => setShowPassword2(v => !v)}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#4a5564', padding: 0, display: 'flex', alignItems: 'center' }}>
                          {showPassword2 ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      }
                    />
                    {form.password_confirm && form.password !== form.password_confirm && (
                      <p style={{ fontSize: 12, color: '#f87171', margin: '6px 0 0 4px' }}>
                        Les mots de passe ne correspondent pas.
                      </p>
                    )}
                  </div>
                  <NavBtn canNext={canNext()} onNext={next} isFirst />
                </div>
              )}

              {/* ── STEP 2 ── */}
              {step === 2 && (
                <div key="s2" className="reg-animate" style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                  <Field label="Adresse e-mail *" icon={Mail} {...fp('email')}
                    type="email" value={form.email} onChange={e => set('email', e.target.value)}
                    placeholder="jean@exemple.fr" required autoComplete="email" />
                  <Field label="Téléphone *" icon={Phone} {...fp('telephone')}
                    type="tel" value={form.telephone} onChange={e => set('telephone', e.target.value)}
                    placeholder="+213 6 00 00 00 00" required autoComplete="tel" />
                  <NavBtn canNext={canNext()} onNext={next} onBack={back} />
                </div>
              )}

              {/* ── STEP 3 ── */}
              {step === 3 && (
                <form key="s3" className="reg-animate" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                  <Field label="Numéro CIN *" icon={CreditCard} {...fp('cin')}
                    value={form.cin} onChange={e => set('cin', e.target.value)}
                    placeholder="AB123456" required />
                  <Field label="Date de naissance *" icon={CalendarDays} {...fp('date_naissance')}
                    type="date" value={form.date_naissance}
                    onChange={e => set('date_naissance', e.target.value)} required />

                  {/* Genre */}
                  <div>
                    <label style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase', color: '#6b7787', display: 'block', marginBottom: 8 }}>
                      Genre *
                    </label>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                      {[['M', 'Homme', '♂'], ['F', 'Femme', '♀']].map(([val, lbl, sym]) => (
                        <button key={val} type="button" onClick={() => set('sexe', val)} style={{
                          padding: '12px', borderRadius: 12, fontSize: 13, fontWeight: 600,
                          cursor: 'pointer', transition: 'all .2s', fontFamily: 'Inter, sans-serif',
                          background: form.sexe === val ? 'rgba(78,181,131,0.12)' : 'rgba(255,255,255,0.04)',
                          border: form.sexe === val ? '1.5px solid rgba(78,181,131,0.35)' : '1.5px solid rgba(255,255,255,0.08)',
                          color: form.sexe === val ? '#4eb583' : '#6b7787',
                          boxShadow: form.sexe === val ? '0 0 0 4px rgba(78,181,131,0.08)' : 'none',
                        }}>
                          <span style={{ marginRight: 6, opacity: 0.7 }}>{sym}</span>{lbl}
                        </button>
                      ))}
                    </div>
                  </div>

                  {error && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '11px 14px', background: 'rgba(212,84,63,0.10)', border: '1px solid rgba(212,84,63,0.25)', borderRadius: 10, color: '#f87171', fontSize: 13 }}>
                      <Activity size={14} style={{ flexShrink: 0 }} /> {error}
                    </div>
                  )}

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2.5fr', gap: 10, marginTop: 4 }}>
                    <BackBtn onBack={back} />
                    <button
                      type="submit"
                      disabled={loading || !form.cin || !form.date_naissance}
                      style={{
                        padding: '13px 16px', borderRadius: 12, border: 0,
                        background: 'linear-gradient(180deg, #4eb583, #1d7f54)',
                        color: 'white', fontSize: 14, fontWeight: 600,
                        cursor: loading ? 'wait' : 'pointer',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                        boxShadow: '0 12px 30px -8px rgba(42,155,105,0.5), inset 0 1px 0 rgba(255,255,255,0.2)',
                        transition: 'transform .15s, box-shadow .2s, opacity .15s',
                        opacity: (loading || !form.cin || !form.date_naissance) ? 0.55 : 1,
                        fontFamily: 'Inter, sans-serif',
                      }}
                      onMouseEnter={e => { if (!loading) { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 16px 36px -8px rgba(42,155,105,0.6), inset 0 1px 0 rgba(255,255,255,0.2)' } }}
                      onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '0 12px 30px -8px rgba(42,155,105,0.5), inset 0 1px 0 rgba(255,255,255,0.2)' }}
                    >
                      {loading
                        ? <span style={{ width: 18, height: 18, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', animation: 'spin 0.7s linear infinite', display: 'inline-block' }} />
                        : <><CheckCircle2 size={17} /> Créer mon compte</>
                      }
                    </button>
                  </div>
                </form>
              )}
            </div>

            <p style={{ textAlign: 'center', fontSize: 13, color: '#6b7787', marginTop: 22 }}>
              Déjà inscrit ?{' '}
              <Link to="/login" style={{ color: '#4eb583', fontWeight: 600, textDecoration: 'none' }}
                onMouseEnter={e => e.currentTarget.style.color = '#87d1a8'}
                onMouseLeave={e => e.currentTarget.style.color = '#4eb583'}>
                Se connecter →
              </Link>
            </p>
          </div>
        </main>
      </div>
    </>
  )
}
