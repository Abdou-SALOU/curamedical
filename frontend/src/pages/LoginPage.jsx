import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import Icon from '../components/Icon'
import Sparkline from '../components/Sparkline'

// ── Intersection-observer reveal hook ──────────────────────────
function useReveal() {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) el.classList.add('in') })
    }, { threshold: 0.15 })
    io.observe(el)
    return () => io.disconnect()
  }, [])
  return ref
}

function Reveal({ children, delay = 0, x = false, className = '' }) {
  const ref = useReveal()
  const cls = `${x ? 'reveal-x' : 'reveal'} ${delay ? `reveal-delay-${delay}` : ''} ${className}`
  return <div ref={ref} className={cls}>{children}</div>
}

// ── Animated counter ───────────────────────────────────────────
function useCount(target, on, dur = 1400) {
  const [v, setV] = useState(0)
  useEffect(() => {
    if (!on) return
    const start = performance.now()
    let raf
    const tick = t => {
      const p = Math.min(1, (t - start) / dur)
      const eased = 1 - Math.pow(1 - p, 3)
      setV(Math.floor(target * eased))
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [on, target, dur])
  return v
}

function CountStat({ value, suffix = '', label }) {
  const ref = useRef(null)
  const [on, setOn] = useState(false)
  useEffect(() => {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) setOn(true) })
    }, { threshold: 0.3 })
    if (ref.current) io.observe(ref.current)
    return () => io.disconnect()
  }, [])
  const n = useCount(value, on)
  const formatted = n >= 1000 ? n.toLocaleString('fr-FR') : n
  return (
    <div ref={ref} className="stat-big">
      <div className="stat-big-value">{formatted}{suffix}</div>
      <div className="stat-big-label">{label}</div>
    </div>
  )
}

// ── Login modal ────────────────────────────────────────────────
function LoginModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPwd, setShowPwd] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(form.username, form.password)
      onSuccess()
    } catch {
      setError('Identifiants incorrects. Veuillez réessayer.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-modal" onClick={onClose}>
      <div className="login-modal-panel" onClick={e => e.stopPropagation()}>
        <div className="auth-panel-cm" style={{ position: 'relative' }}>
          <button className="login-close" onClick={onClose}>
            <Icon name="x" size={16} stroke={2} />
          </button>

          <h2 style={{ fontSize: 28, fontWeight: 700, letterSpacing: '-0.02em', margin: '0 0 6px', color: 'white' }}>
            Bon retour 👋
          </h2>
          <p style={{ fontSize: 14, color: '#98a3b1', marginBottom: 28 }}>
            Accédez à votre espace professionnel sécurisé.
          </p>

          <form onSubmit={handleSubmit}>
            <div className="auth-label-cm"><span>Identifiant</span></div>
            <div className="auth-field-cm">
              <span className="ico-left"><Icon name="user" size={16} /></span>
              <input
                className="auth-input-cm"
                value={form.username}
                onChange={e => setForm({ ...form, username: e.target.value })}
                placeholder="Nom d'utilisateur"
                required
                autoFocus
              />
            </div>

            <div className="auth-label-cm">
              <span>Mot de passe</span>
            </div>
            <div className="auth-field-cm">
              <span className="ico-left"><Icon name="lock" size={16} /></span>
              <input
                className="auth-input-cm"
                type={showPwd ? 'text' : 'password'}
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                placeholder="••••••••"
                required
              />
              <button type="button" className="ico-right" onClick={() => setShowPwd(!showPwd)}>
                <Icon name={showPwd ? 'eyeOff' : 'eye'} size={16} />
              </button>
            </div>

            {error && (
              <div style={{
                display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px',
                background: 'rgba(212,84,63,0.12)', border: '1px solid rgba(212,84,63,0.3)',
                borderRadius: 10, color: '#f87171', fontSize: 13, marginBottom: 16,
              }}>
                <Icon name="x" size={14} stroke={2.5} /> {error}
              </div>
            )}

            <button type="submit" className="auth-cta-cm" disabled={loading} style={{ marginTop: 8 }}>
              {loading
                ? <span style={{ width: 18, height: 18, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', animation: 'spin 0.7s linear infinite', display: 'inline-block' }} />
                : <><Icon name="chevron" size={15} /> Accéder à la plateforme</>
              }
            </button>
          </form>

          <div style={{
            display: 'flex', alignItems: 'center', gap: 8, marginTop: 20,
            padding: '10px 14px',
            background: 'rgba(78,181,131,0.06)', border: '1px solid rgba(78,181,131,0.16)',
            borderRadius: 10, color: 'var(--brand-200)', fontSize: 11, lineHeight: 1.5,
          }}>
            <Icon name="lock" size={13} />
            <span>Accès réservé aux professionnels autorisés. Toutes les actions sont journalisées.</span>
          </div>

          {/* Register link for patients */}
          <div style={{ marginTop: 16, textAlign: 'center', fontSize: 13, color: '#6b7787' }}>
            Vous êtes patient ?{' '}
            <a
              href="/register"
              style={{ color: 'var(--brand-300)', fontWeight: 600, textDecoration: 'none' }}
              onMouseEnter={e => e.currentTarget.style.color = 'var(--brand-200)'}
              onMouseLeave={e => e.currentTarget.style.color = 'var(--brand-300)'}
            >
              Créer votre espace santé →
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Brand mark ────────────────────────────────────────────────
function BrandMark({ size = 40 }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: size * 0.275,
      background: 'linear-gradient(140deg, var(--brand-300), var(--brand-600))',
      display: 'grid', placeItems: 'center', color: 'white',
      boxShadow: '0 8px 30px rgba(42,155,105,0.4), inset 0 1px 0 rgba(255,255,255,0.25)',
    }}>
      <svg width={size * 0.55} height={size * 0.55} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2 4 6v6c0 5 3.5 9 8 10 4.5-1 8-5 8-10V6l-8-4Z" />
        <path d="M9 11h6M12 8v6" />
      </svg>
    </div>
  )
}

// ── Main landing page ──────────────────────────────────────────
export default function LoginPage() {
  const navigate = useNavigate()
  const [showLogin, setShowLogin] = useState(false)
  const [activeSection, setActiveSection] = useState(0)
  const scrollRef = useRef(null)

  useEffect(() => {
    const root = scrollRef.current
    if (!root) return
    const sections = root.querySelectorAll('.land-section')
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) setActiveSection(parseInt(e.target.dataset.idx))
      })
    }, { threshold: 0.5, root })
    sections.forEach(s => io.observe(s))
    return () => io.disconnect()
  }, [])

  const scrollTo = idx => {
    const root = scrollRef.current
    if (!root) return
    root.querySelectorAll('.land-section')[idx]?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const handleSuccess = () => {
    setShowLogin(false)
    navigate('/')
  }

  const SPARKLINE_DATA = [12, 18, 22, 19, 28, 24, 31, 27, 34, 29, 38, 42]

  return (
    <>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      <div ref={scrollRef} className="landing">
        <div className="land-bg" />

        {/* ── Top nav ── */}
        <nav className="land-nav">
          <div className="land-nav-brand">
            <BrandMark size={38} />
            <div>
              <div style={{ fontSize: 16, fontWeight: 700, color: 'white' }}>CuraMedical</div>
              <div style={{ fontSize: 9, color: '#98a3b1', textTransform: 'uppercase', letterSpacing: '0.16em', marginTop: 1 }}>Système médical IA</div>
            </div>
          </div>
          <div className="land-nav-links">
            <button className="land-nav-link" onClick={() => scrollTo(1)}>Fonctionnalités</button>
            <button className="land-nav-link" onClick={() => scrollTo(2)}>Chiffres clés</button>
            <button className="land-nav-link" onClick={() => scrollTo(3)}>Workflow</button>
            <button className="land-nav-link" onClick={() => scrollTo(4)}>Sécurité</button>
          </div>
          <button className="land-nav-cta" onClick={() => setShowLogin(true)}>
            Connexion <Icon name="chevron" size={13} />
          </button>
        </nav>

        {/* ── Section dots ── */}
        <div className="land-dots">
          {[0, 1, 2, 3, 4].map(i => (
            <button key={i} className={`land-dot ${activeSection === i ? 'active' : ''}`} onClick={() => scrollTo(i)} />
          ))}
        </div>

        {/* ── Section 0: Hero ── */}
        <section className="land-section" data-idx="0">
          <div className="land-hero">
            <div>
              <Reveal>
                <div className="land-eyebrow">
                  <span className="live-dot" /> Nouvelle version · v3.2 · 2026
                </div>
              </Reveal>
              <Reveal delay={1}>
                <h1 className="land-h1">
                  La plateforme<br />médicale <span className="accent">augmentée</span> par l'IA.
                </h1>
              </Reveal>
              <Reveal delay={2}>
                <p className="land-lead">
                  CuraMedical unifie consultations, dossiers patients, ordonnances et téléconsultation dans un flux de travail fluide et chiffré de bout en bout.
                </p>
              </Reveal>
              <Reveal delay={3}>
                <div className="land-cta-row">
                  <button className="land-btn-primary" onClick={() => setShowLogin(true)}>
                    Accéder à la plateforme <Icon name="chevron" size={15} />
                  </button>
                  <button className="land-btn-ghost" onClick={() => scrollTo(1)}>
                    <Icon name="play" size={13} /> Découvrir
                  </button>
                </div>
              </Reveal>
              <Reveal delay={4}>
                <div style={{ display: 'flex', gap: 24, marginTop: 40, alignItems: 'center' }}>
                  <div style={{ display: 'flex' }}>
                    {['#2a9b69', '#4178d6', '#c98b1e', '#6a5acd'].map((c, i) => (
                      <div key={i} style={{ width: 32, height: 32, borderRadius: '50%', background: c, border: '2px solid #06090d', marginLeft: i ? -10 : 0 }} />
                    ))}
                  </div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'white' }}>1 800+ praticiens</div>
                    <div style={{ fontSize: 11, color: '#98a3b1' }}>nous font déjà confiance</div>
                  </div>
                </div>
              </Reveal>
            </div>

            <Reveal x>
              <div className="land-preview-wrap">
                <div className="land-preview">
                  <div className="land-preview-head">
                    <span className="land-preview-dot" style={{ background: '#d4543f' }} />
                    <span className="land-preview-dot" style={{ background: '#c98b1e' }} />
                    <span className="land-preview-dot" style={{ background: 'var(--brand-400)' }} />
                    <span style={{ marginLeft: 'auto', fontSize: 10, color: '#6b7787', fontFamily: 'var(--font-mono)' }}>cura.app / dashboard</span>
                  </div>
                  <div className="land-preview-grid">
                    <div className="land-mini-card">
                      <div className="land-mini-eyebrow">Consultations</div>
                      <div className="land-mini-value">324</div>
                      <div className="land-mini-delta">↑ +12.4%</div>
                      <div style={{ marginTop: 8 }}>
                        <Sparkline data={SPARKLINE_DATA} height={36} width={180} color="#4eb583" />
                      </div>
                    </div>
                    <div className="land-mini-card">
                      <div className="land-mini-eyebrow">Adoption IA</div>
                      <div className="land-mini-value">64%</div>
                      <div className="land-mini-delta">↑ +8.1%</div>
                      <div style={{ height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 2, marginTop: 14, overflow: 'hidden' }}>
                        <div style={{ width: '64%', height: '100%', background: 'linear-gradient(90deg, var(--brand-400), var(--brand-300))' }} />
                      </div>
                    </div>
                    <div className="land-mini-card" style={{ gridColumn: '1 / -1' }}>
                      <div className="land-mini-eyebrow">Rendez-vous · Aujourd'hui</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
                        {[
                          { t: '08:30', p: 'K. Bensalem', s: 'Confirmé' },
                          { t: '09:15', p: 'A. Tazi', s: 'Téléconsult.' },
                          { t: '10:00', p: 'Y. El Idrissi', s: 'En cours' },
                        ].map((r, i) => (
                          <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 12, padding: '6px 0', borderBottom: i < 2 ? '1px solid rgba(255,255,255,0.05)' : '0' }}>
                            <span style={{ fontFamily: 'var(--font-mono)', color: '#98a3b1' }}>{r.t}</span>
                            <span style={{ color: 'white', fontWeight: 500 }}>{r.p}</span>
                            <span style={{ fontSize: 10, color: 'var(--brand-300)', fontWeight: 600 }}>{r.s}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="float-chip float-chip-1">
                  <div className="float-ico"><Icon name="sparkle" size={14} /></div>
                  <div>
                    <div style={{ fontWeight: 600 }}>Diagnostic IA</div>
                    <div style={{ color: '#98a3b1', fontSize: 10 }}>92% confiance</div>
                  </div>
                </div>
                <div className="float-chip float-chip-2">
                  <div className="float-ico"><Icon name="shield" size={14} /></div>
                  <div style={{ fontWeight: 600 }}>Chiffré E2E</div>
                </div>
                <div className="float-chip float-chip-3">
                  <div className="float-ico"><Icon name="video" size={14} /></div>
                  <div>
                    <div style={{ fontWeight: 600 }}>Téléconsult.</div>
                    <div style={{ color: '#98a3b1', fontSize: 10 }}>12 ms latence</div>
                  </div>
                </div>
              </div>
            </Reveal>
          </div>
        </section>

        {/* ── Section 1: Features ── */}
        <section className="land-section" data-idx="1">
          <div style={{ width: '100%' }}>
            <Reveal><div className="land-eyebrow" style={{ marginBottom: 18 }}>Fonctionnalités</div></Reveal>
            <Reveal delay={1}><h2 className="sec-title">Tout ce qu'il faut, <span className="land-accent">rien de superflu</span>.</h2></Reveal>
            <Reveal delay={2}><p className="sec-lead">Un système conçu avec et pour les professionnels de santé. Chaque écran sert le geste clinique.</p></Reveal>
            <div className="land-features">
              {[
                { ico: 'stethoscope', n: '01', t: 'Suivi clinique complet', s: 'Consultations, examens, prescriptions et historiques centralisés dans un dossier unique.' },
                { ico: 'sparkle',     n: '02', t: 'Assistant IA intégré',   s: 'Aide au diagnostic, suggestion d\'examens et alertes contextuelles basées sur des modèles validés.' },
                { ico: 'video',       n: '03', t: 'Téléconsultation HD',    s: 'Salles vidéo chiffrées E2E, enregistrement sécurisé, partage d\'écran et chat médical.' },
                { ico: 'calendar',    n: '04', t: 'Planning intelligent',   s: 'Réservation patient, rappels SMS automatisés et synchronisation multi-praticiens.' },
                { ico: 'file',        n: '05', t: 'Ordonnances numériques', s: 'Prescription assistée avec base médicamenteuse, interactions et signature électronique.' },
                { ico: 'shield',      n: '06', t: 'Conformité HDS & RGPD',  s: 'Hébergement de données de santé certifié, journalisation complète, droits patients respectés.' },
              ].map((f, i) => (
                <Reveal key={f.n} delay={(i % 3) + 1}>
                  <div className="feat-card">
                    <span className="feat-num">{f.n}</span>
                    <div className="feat-ico"><Icon name={f.ico} size={22} /></div>
                    <div className="feat-title">{f.t}</div>
                    <div className="feat-text">{f.s}</div>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ── Section 2: Stats ── */}
        <section className="land-section" data-idx="2">
          <div style={{ width: '100%' }}>
            <Reveal><div className="land-eyebrow" style={{ marginBottom: 18 }}>Chiffres clés</div></Reveal>
            <Reveal delay={1}><h2 className="sec-title">L'impact en <span className="land-accent">chiffres</span>.</h2></Reveal>
            <Reveal delay={2}><p className="sec-lead">Mesures consolidées sur l'ensemble des cabinets utilisateurs en 2026.</p></Reveal>
            <div className="land-stats">
              <Reveal delay={1}><CountStat value={1847} label="Praticiens actifs sur la plateforme" /></Reveal>
              <Reveal delay={2}><CountStat value={284000} label="Consultations enregistrées en 2026" /></Reveal>
              <Reveal delay={3}><CountStat value={64} suffix="%" label="Taux d'adoption de l'assistant IA" /></Reveal>
              <Reveal delay={4}><CountStat value={99} suffix=".98%" label="Disponibilité du service (SLA)" /></Reveal>
            </div>
          </div>
        </section>

        {/* ── Section 3: Workflow ── */}
        <section className="land-section" data-idx="3">
          <div style={{ width: '100%' }}>
            <Reveal><div className="land-eyebrow" style={{ marginBottom: 18 }}>Workflow</div></Reveal>
            <Reveal delay={1}><h2 className="sec-title">De l'accueil à <span className="land-accent">la prescription</span>.</h2></Reveal>
            <Reveal delay={2}><p className="sec-lead">Un parcours unifié, conçu pour réduire la charge administrative et augmenter le temps clinique.</p></Reveal>
            <div className="land-flow">
              {[
                { t: 'Accueil patient',  s: 'Création de dossier en moins de 60 secondes. Carte vitale intégrée.' },
                { t: 'Consultation',     s: 'Capture des symptômes, examen structuré, suggestions IA en temps réel.' },
                { t: 'Diagnostic',       s: 'Synthèse, code CIM-10 auto-suggéré et plan thérapeutique.' },
                { t: 'Prescription',     s: 'Ordonnance numérique signée, transmise à la pharmacie du patient.' },
              ].map((f, i) => (
                <Reveal key={f.t} delay={(i % 4) + 1}>
                  <div className="flow-step">
                    <div className="flow-num">{String(i + 1).padStart(2, '0')}</div>
                    <div className="flow-title">{f.t}</div>
                    <div className="flow-text">{f.s}</div>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ── Section 4: CTA final ── */}
        <section className="land-section" data-idx="4">
          <div className="land-cta-final">
            <Reveal><div className="land-eyebrow" style={{ marginBottom: 18 }}>Prêt à commencer ?</div></Reveal>
            <Reveal delay={1}>
              <div className="land-cta-card">
                <h2 className="sec-title" style={{ marginBottom: 12 }}>
                  Pilotez votre cabinet<br />avec <span className="land-accent">précision</span>.
                </h2>
                <p className="sec-lead" style={{ margin: '0 auto 32px' }}>
                  Rejoignez les 1 800+ praticiens qui utilisent CuraMedical au quotidien.
                </p>
                <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                  <button className="land-btn-primary" onClick={() => setShowLogin(true)}>
                    Accéder à la plateforme <Icon name="chevron" size={15} />
                  </button>
                  <button className="land-btn-ghost">
                    <Icon name="phone" size={13} /> Demander une démo
                  </button>
                </div>
                <div style={{ display: 'flex', gap: 18, alignItems: 'center', justifyContent: 'center', marginTop: 40, flexWrap: 'wrap' }}>
                  {[['shield', 'HDS'], ['lock', 'RGPD'], ['check', 'ISO 27001'], ['badge', 'ANSM']].map(([ico, lbl]) => (
                    <div key={lbl} className="auth-trust-item-cm">
                      <Icon name={ico} size={12} /> {lbl}
                    </div>
                  ))}
                </div>
              </div>
            </Reveal>
            <div style={{ marginTop: 48, fontSize: 11, color: '#4a5564', fontFamily: 'var(--font-mono)' }}>
              © 2026 CuraMedical · v3.2 · build 2026.05
            </div>
          </div>
        </section>
      </div>

      {showLogin && (
        <LoginModal onClose={() => setShowLogin(false)} onSuccess={handleSuccess} />
      )}
    </>
  )
}
