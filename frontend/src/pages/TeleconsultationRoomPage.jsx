import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import useAuthStore from '../store/authStore'
import Icon from '../components/Icon'

/* ── Symptômes ────────────────────────────────────────────────── */
const SYMPTOMS = [
  { value: 'fever',               label: 'Fièvre',                   hint: 'Température élevée ou frissons.' },
  { value: 'high_fever',          label: 'Fièvre élevée',            hint: 'Température > 39°C.' },
  { value: 'mild_fever',          label: 'Fièvre légère',            hint: 'Température 37.5–38.5°C.' },
  { value: 'chills',              label: 'Frissons',                  hint: 'Sensations de froid intenses.' },
  { value: 'sweating',            label: 'Transpiration excessive',   hint: 'Sueurs nocturnes ou diurnes.' },
  { value: 'fatigue',             label: 'Fatigue / Asthénie',        hint: 'Épuisement inhabituel.' },
  { value: 'cough',               label: 'Toux',                      hint: 'Toux sèche ou grasse.' },
  { value: 'breathlessness',      label: 'Dyspnée',                   hint: 'Essoufflement ou difficulté à respirer.' },
  { value: 'chest_pain',          label: 'Douleur thoracique',        hint: 'Oppression ou douleur poitrine.' },
  { value: 'headache',            label: 'Céphalées',                 hint: 'Maux de tête, migraines.' },
  { value: 'dizziness',           label: 'Vertiges',                  hint: 'Sensation de tournis.' },
  { value: 'nausea',              label: 'Nausées',                   hint: 'Envie de vomir.' },
  { value: 'vomiting',            label: 'Vomissements',              hint: 'Vomissements actifs.' },
  { value: 'diarrhoea',           label: 'Diarrhée',                  hint: 'Selles liquides fréquentes.' },
  { value: 'abdominal_pain',      label: 'Douleur abdominale',        hint: 'Crampes ou douleurs au ventre.' },
  { value: 'stomach_pain',        label: 'Douleur gastrique',         hint: 'Douleurs à l\'estomac.' },
  { value: 'constipation',        label: 'Constipation',              hint: 'Difficultés à aller à la selle.' },
  { value: 'back_pain',           label: 'Douleur dorsale',           hint: 'Douleurs lombaires ou dorsales.' },
  { value: 'joint_pain',          label: 'Douleurs articulaires',     hint: 'Douleurs dans les articulations.' },
  { value: 'muscle_pain',         label: 'Myalgies',                  hint: 'Douleurs musculaires, courbatures.' },
  { value: 'neck_stiffness',      label: 'Raideur de nuque',          hint: 'Difficulté à tourner la tête.' },
  { value: 'skin_rash',           label: 'Éruption cutanée',          hint: 'Rougeurs, boutons, plaques.' },
  { value: 'itching',             label: 'Démangeaisons',             hint: 'Prurit généralisé ou localisé.' },
  { value: 'yellowish_skin',      label: 'Jaunisse',                  hint: 'Ictère cutané ou oculaire.' },
  { value: 'weight_loss',         label: 'Perte de poids',            hint: 'Amaigrissement inexpliqué.' },
  { value: 'loss_of_appetite',    label: 'Anorexie',                  hint: 'Refus ou perte d\'appétit.' },
  { value: 'swollen_lymph_nodes', label: 'Ganglions gonflés',         hint: 'Adénopathie.' },
  { value: 'runny_nose',          label: 'Rhinorrhée',                hint: 'Écoulement nasal.' },
  { value: 'throat_irritation',   label: 'Mal de gorge',              hint: 'Pharyngite, irritation.' },
  { value: 'redness_of_eyes',     label: 'Yeux rouges',              hint: 'Conjonctivite ou irritation.' },
  { value: 'fast_heart_rate',     label: 'Tachycardie',               hint: 'Cœur qui bat trop vite.' },
]

const EMPTY_FORM = {
  symptomes: [], examen_clinique: '', diagnostic: '', notes: '',
  suggestions_ia: null, ia_utilisee: false,
}
const EMPTY_IA = { age: '', gender: 'M', blood_pressure: 'Normal', cholesterol: 'Normal' }

/* ── Light theme tokens (cohérent avec le reste de l'application) ─ */
const D = {
  bg:        '#f1f5f9',
  card:      '#ffffff',
  cardAlt:   '#f8fafc',
  border:    'rgba(15,23,42,0.08)',
  borderMed: 'rgba(15,23,42,0.16)',
  textPrim:  '#0f172a',
  textSec:   '#64748b',
  textMuted: '#94a3b8',
  brand:     '#059669',
  brandDim:  'rgba(5,150,105,0.10)',
  brandBord: 'rgba(5,150,105,0.30)',
  warn:      '#d97706',
  danger:    '#dc2626',
}

/* ── Section header ───────────────────────────────────────────── */
function SectionLabel({ icon, children }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 8,
      fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
      letterSpacing: '0.15em', color: D.brand,
      marginBottom: 10,
    }}>
      <Icon name={icon} size={12} />
      {children}
      <span style={{ flex: 1, height: 1, background: D.border }} />
    </div>
  )
}

/* ── Main page ────────────────────────────────────────────────── */
export default function TeleconsultationRoomPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const [appt, setAppt]           = useState(null)
  const [loading, setLoading]     = useState(true)
  const [form, setForm]           = useState(EMPTY_FORM)
  const [iaParams, setIaParams]   = useState(EMPTY_IA)
  const [iaLoading, setIaLoading] = useState(false)
  const [iaError, setIaError]     = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone]           = useState(false)
  const [searchSym, setSearchSym] = useState('')

  useEffect(() => {
    api.get(`/api/appointments/${id}/`)
      .then(r => {
        setAppt(r.data)
        const p = r.data.patient_detail
        if (p) {
          setIaParams(prev => ({
            ...prev,
            age: p.age ?? 30,
            gender: p.sexe === 'F' ? 'F' : 'M',
          }))
        }
      })
      .catch(() => { toast.error('Rendez-vous introuvable.'); navigate('/appointments') })
      .finally(() => setLoading(false))
  }, [id, navigate])

  const toggleSymptom = useCallback(v => {
    setForm(f => ({
      ...f,
      symptomes: f.symptomes.includes(v)
        ? f.symptomes.filter(s => s !== v)
        : [...f.symptomes, v],
    }))
  }, [])

  const handleAskIA = async () => {
    if (form.symptomes.length === 0) {
      setIaError('Sélectionnez au moins un symptôme.')
      return
    }
    setIaLoading(true); setIaError('')
    try {
      const { data } = await api.post('/api/consultations/suggestions-ia/', {
        symptomes: form.symptomes,
        age: iaParams.age,
        gender: iaParams.gender,
        blood_pressure: iaParams.blood_pressure,
        cholesterol: iaParams.cholesterol,
      })
      const suggestions = data.suggestions || []
      setForm(f => ({
        ...f,
        suggestions_ia: suggestions,
        ia_utilisee: suggestions.length > 0,
        diagnostic: suggestions[0]?.disease || f.diagnostic,
      }))
      if (suggestions.length === 0) setIaError('Aucune suggestion disponible pour ces paramètres.')
    } catch {
      setIaError('Service IA indisponible. Vérifiez que le service est démarré.')
    } finally {
      setIaLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!form.diagnostic.trim()) {
      toast.error('Le diagnostic est requis avant de terminer.')
      return
    }
    setSubmitting(true)
    try {
      await api.post('/api/consultations/', {
        rendez_vous: parseInt(id, 10),
        symptomes: form.symptomes,
        examen_clinique: form.examen_clinique,
        diagnostic: form.diagnostic,
        notes: form.notes,
        suggestions_ia: form.suggestions_ia,
        ia_utilisee: form.ia_utilisee,
      })
      // Met à jour le statut du RDV à TERMINE
      await api.patch(`/api/appointments/${id}/update-statut/`, { statut: 'TERMINE' })
      setDone(true)
    } catch (err) {
      const detail = err.response?.data
      const msg = typeof detail === 'object'
        ? Object.values(detail).flat()[0]
        : 'Erreur lors de la création de la consultation.'
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  /* ── Loading ── */
  if (loading) return (
    <div style={{ position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f1f5f9' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div style={{ width: 40, height: 40, borderRadius: '50%', border: '3px solid rgba(5,150,105,0.2)', borderTopColor: 'var(--brand-500)', animation: 'spin 0.8s linear infinite' }} />
        <p style={{ color: '#64748b', fontSize: 14 }}>Chargement de la salle…</p>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )

  /* ── Success screen ── */
  if (done) return (
    <div style={{ position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-app)', flexDirection: 'column', gap: 24 }}>
      <div style={{ width: 72, height: 72, borderRadius: '50%', background: 'var(--brand-50)', display: 'grid', placeItems: 'center', color: 'var(--brand-600)' }}>
        <Icon name="check" size={36} stroke={2.5} />
      </div>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--ink-900)', letterSpacing: '-0.02em', marginBottom: 8 }}>
          Consultation terminée
        </div>
        <div style={{ fontSize: 14, color: 'var(--ink-500)', maxWidth: 420, lineHeight: 1.6 }}>
          Le compte-rendu a été enregistré et un mail de synthèse a été envoyé automatiquement à{' '}
          <strong style={{ color: 'var(--ink-700)' }}>{appt?.patient_detail?.nom_complet || 'votre patient'}</strong>.
        </div>
      </div>
      <div style={{ display: 'flex', gap: 12 }}>
        <button className="cm-btn cm-btn-ghost" onClick={() => navigate('/appointments')}>
          <Icon name="calendar" size={14} /> Retour aux rendez-vous
        </button>
        <button className="cm-btn cm-btn-brand" onClick={() => navigate('/consultations')}>
          <Icon name="stethoscope" size={14} /> Voir les consultations
        </button>
      </div>
    </div>
  )

  const displayName = user
    ? encodeURIComponent(`Dr. ${user.last_name || user.username}`)
    : 'Médecin'
  const jitsiUrl = `https://meet.jit.si/${appt?.lien_visio}#config.prejoinPageEnabled=false&config.startWithAudioMuted=false&userInfo.displayName="${displayName}"`
  const filteredSymptoms = SYMPTOMS.filter(s =>
    !searchSym || s.label.toLowerCase().includes(searchSym.toLowerCase())
  )

  const inputStyle = {
    width: '100%', boxSizing: 'border-box',
    background: D.cardAlt, border: `1px solid ${D.borderMed}`,
    borderRadius: 8, padding: '8px 12px',
    color: D.textPrim, fontSize: 13,
    outline: 'none', fontFamily: 'var(--font-sans)',
  }
  const labelStyle = {
    fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
    letterSpacing: '0.1em', color: D.textSec, marginBottom: 5, display: 'block',
  }

  return (
    <div style={{
      position: 'fixed', inset: 0,
      display: 'grid', gridTemplateRows: '50px 1fr',
      background: '#e2e8f0', fontFamily: 'var(--font-sans)',
    }}>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes livePulse { 0%,100%{opacity:1} 50%{opacity:.4} }
        .dark-scroll::-webkit-scrollbar { width: 4px; }
        .dark-scroll::-webkit-scrollbar-track { background: transparent; }
        .dark-scroll::-webkit-scrollbar-thumb { background: rgba(15,23,42,0.15); border-radius: 4px; }
        .dark-scroll::-webkit-scrollbar-thumb:hover { background: rgba(15,23,42,0.28); }
      `}</style>

      {/* ── Top bar ── */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 20px', borderBottom: `1px solid ${D.border}`,
        background: D.card,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <button
            onClick={() => navigate('/appointments')}
            style={{ display: 'flex', alignItems: 'center', gap: 5, color: D.textSec, background: 'none', border: 'none', cursor: 'pointer', fontSize: 13, padding: '4px 8px', borderRadius: 6 }}
          >
            <Icon name="chevron" size={14} style={{ transform: 'rotate(180deg)' }} />
            Retour
          </button>
          <div style={{ width: 1, height: 18, background: D.border }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
            <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#ef4444', animation: 'livePulse 1.6s ease-in-out infinite' }} />
            <span style={{ fontSize: 12, color: '#dc2626', fontWeight: 700, letterSpacing: '0.05em' }}>EN DIRECT</span>
          </div>
          <div style={{ fontSize: 13, color: D.textSec }}>
            <span style={{ color: D.textPrim, fontWeight: 600 }}>{appt?.patient_detail?.nom_complet}</span>
            {appt?.date_heure && <span> · {new Date(appt.date_heure).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}</span>}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 11, color: D.textMuted, fontFamily: 'var(--font-mono)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            {appt?.lien_visio}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '4px 10px', borderRadius: 999, background: 'rgba(78,181,131,0.1)', border: `1px solid ${D.brandBord}`, color: D.brand, fontSize: 11, fontWeight: 600 }}>
            <Icon name="lock" size={11} /> Chiffré E2E
          </div>
        </div>
      </div>

      {/* ── Main content ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '58% 42%', overflow: 'hidden' }}>

        {/* LEFT: Jitsi (tuile vidéo — fond sombre neutre, standard pour la visio) */}
        <div style={{ background: '#0f172a', position: 'relative' }}>
          <iframe
            src={jitsiUrl}
            allow="camera; microphone; fullscreen; display-capture; autoplay"
            style={{ width: '100%', height: '100%', border: 0 }}
            title="Téléconsultation"
          />
        </div>

        {/* RIGHT: Consultation form */}
        <div style={{
          background: D.bg,
          display: 'flex', flexDirection: 'column',
          borderLeft: `1px solid ${D.border}`,
          overflow: 'hidden',
        }}>

          {/* ── Panel header ── */}
          <div style={{ padding: '14px 18px', borderBottom: `1px solid ${D.border}`, background: D.card, flexShrink: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <div>
                <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.15em', color: D.brand, marginBottom: 3 }}>
                  Consultation en cours
                </div>
                <div style={{ fontSize: 17, fontWeight: 700, color: D.textPrim, letterSpacing: '-0.01em' }}>
                  {appt?.patient_detail?.nom_complet}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: D.textSec, padding: '5px 10px', borderRadius: 999, background: D.cardAlt, border: `1px solid ${D.border}` }}>
                <Icon name="mail" size={12} /> Mail auto à la fin
              </div>
            </div>
            {/* Badges patient */}
            {appt?.patient_detail && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {[
                  { icon: '👤', label: 'Âge', value: `${appt.patient_detail.age} ans` },
                  { icon: '⚧', label: 'Sexe', value: appt.patient_detail.sexe === 'F' ? 'Féminin' : 'Masculin' },
                  appt.patient_detail.groupe_sanguin && { icon: '🩸', label: 'Groupe', value: appt.patient_detail.groupe_sanguin },
                  appt.patient_detail.telephone && { icon: '📞', label: 'Tél.', value: appt.patient_detail.telephone },
                ].filter(Boolean).map(item => (
                  <div key={item.label} style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    padding: '4px 11px', borderRadius: 999,
                    background: D.cardAlt, border: `1px solid ${D.borderMed}`,
                    fontSize: 12,
                  }}>
                    <span style={{ color: D.textSec }}>{item.label}</span>
                    <span style={{ color: D.textPrim, fontWeight: 700 }}>{item.value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* ── Scrollable form ── */}
          <div className="dark-scroll" style={{ flex: 1, overflowY: 'auto', padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: 18 }}>

            {/* Symptômes */}
            <div>
              <SectionLabel icon="stethoscope">Symptômes</SectionLabel>
              <input
                style={{ ...inputStyle, marginBottom: 10 }}
                placeholder="Rechercher un symptôme…"
                value={searchSym}
                onChange={e => setSearchSym(e.target.value)}
              />
              <div className="dark-scroll" style={{ display: 'flex', flexWrap: 'wrap', gap: 5, maxHeight: 165, overflowY: 'auto', paddingRight: 2 }}>
                {filteredSymptoms.map(s => {
                  const active = form.symptomes.includes(s.value)
                  return (
                    <button
                      key={s.value}
                      onClick={() => toggleSymptom(s.value)}
                      title={s.hint}
                      style={{
                        padding: '5px 12px', borderRadius: 999, fontSize: 12, fontWeight: 600, cursor: 'pointer',
                        border: active ? `1px solid ${D.brandBord}` : `1px solid ${D.borderMed}`,
                        background: active ? D.brandDim : D.cardAlt,
                        color: active ? D.brand : D.textSec,
                        transition: 'all .12s',
                        fontFamily: 'var(--font-sans)',
                        outline: 'none',
                      }}
                    >
                      {active ? `✓ ${s.label}` : s.label}
                    </button>
                  )
                })}
              </div>
              {form.symptomes.length > 0 && (
                <div style={{ marginTop: 8, fontSize: 11, color: D.brand, fontWeight: 600 }}>
                  {form.symptomes.length} symptôme{form.symptomes.length > 1 ? 's' : ''} sélectionné{form.symptomes.length > 1 ? 's' : ''}
                </div>
              )}
            </div>

            {/* IA Module */}
            <div style={{ background: D.card, borderRadius: 12, padding: 16, border: `1px solid ${D.brandBord}` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, fontWeight: 700, color: D.brand, marginBottom: 14 }}>
                <Icon name="sparkle" size={14} /> Assistant IA — Aide au diagnostic
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
                <div>
                  <label style={labelStyle}>Âge</label>
                  <input
                    style={inputStyle} type="number"
                    value={iaParams.age}
                    onChange={e => setIaParams(p => ({ ...p, age: e.target.value }))}
                    placeholder="ex: 30"
                  />
                </div>
                <div>
                  <label style={labelStyle}>Genre</label>
                  <select style={{ ...inputStyle, cursor: 'pointer' }} value={iaParams.gender} onChange={e => setIaParams(p => ({ ...p, gender: e.target.value }))}>
                    <option value="M">Masculin</option>
                    <option value="F">Féminin</option>
                  </select>
                </div>
                <div style={{ gridColumn: '1 / -1' }}>
                  <label style={labelStyle}>Tension artérielle</label>
                  <select style={{ ...inputStyle, cursor: 'pointer' }} value={iaParams.blood_pressure} onChange={e => setIaParams(p => ({ ...p, blood_pressure: e.target.value }))}>
                    <option value="Normal">Normale</option>
                    <option value="High">Élevée</option>
                    <option value="Low">Basse</option>
                  </select>
                </div>
              </div>
              <button
                onClick={handleAskIA}
                disabled={iaLoading}
                style={{
                  width: '100%', padding: '10px 0', borderRadius: 8, border: 'none',
                  background: iaLoading ? 'rgba(78,181,131,0.4)' : D.brand,
                  color: '#ffffff', fontWeight: 700, fontSize: 13, cursor: iaLoading ? 'wait' : 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
                  fontFamily: 'var(--font-sans)', transition: 'opacity .15s',
                }}
              >
                {iaLoading
                  ? <><span style={{ width: 13, height: 13, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.4)', borderTopColor: '#ffffff', animation: 'spin 0.7s linear infinite', display: 'inline-block' }} /> Analyse en cours…</>
                  : <><Icon name="sparkle" size={14} /> Analyser avec l'IA</>
                }
              </button>
              {iaError && (
                <div style={{ marginTop: 9, fontSize: 12, color: '#b91c1c', display: 'flex', alignItems: 'center', gap: 6, padding: '8px 10px', background: 'rgba(239,68,68,0.08)', borderRadius: 7, border: '1px solid rgba(239,68,68,0.25)' }}>
                  <Icon name="x" size={12} stroke={2.5} />{iaError}
                </div>
              )}
              {form.suggestions_ia?.length > 0 && (
                <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {form.suggestions_ia.slice(0, 3).map((s, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      padding: '10px 13px', borderRadius: 9,
                      background: i === 0 ? 'rgba(78,181,131,0.12)' : D.cardAlt,
                      border: i === 0 ? `1px solid ${D.brandBord}` : `1px solid ${D.border}`,
                    }}>
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 700, color: i === 0 ? D.brand : D.textPrim }}>{s.disease}</div>
                        {i === 0 && <div style={{ fontSize: 10, color: D.textSec, marginTop: 2, fontStyle: 'italic' }}>Diagnostic principal suggéré</div>}
                      </div>
                      <div style={{
                        padding: '3px 10px', borderRadius: 999, fontSize: 11, fontWeight: 700, minWidth: 48, textAlign: 'center',
                        background: s.confidence > 70 ? 'rgba(5,150,105,0.16)' : s.confidence > 30 ? 'rgba(245,158,11,0.18)' : 'rgba(15,23,42,0.06)',
                        color: s.confidence > 70 ? D.brand : s.confidence > 30 ? '#f59e0b' : D.textSec,
                        border: `1px solid ${s.confidence > 70 ? D.brandBord : s.confidence > 30 ? 'rgba(245,158,11,0.3)' : D.border}`,
                      }}>
                        {Math.round(s.confidence)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Examen clinique */}
            <div>
              <SectionLabel icon="file">Examen clinique</SectionLabel>
              <textarea
                style={{ ...inputStyle, resize: 'vertical', lineHeight: 1.6, minHeight: 80 }}
                rows={3}
                placeholder="Auscultation, palpation, examen physique…"
                value={form.examen_clinique}
                onChange={e => setForm(f => ({ ...f, examen_clinique: e.target.value }))}
              />
            </div>

            {/* Diagnostic */}
            <div>
              <SectionLabel icon="brain">Diagnostic</SectionLabel>
              <textarea
                style={{
                  ...inputStyle, resize: 'vertical', lineHeight: 1.6, minHeight: 80,
                  borderColor: form.diagnostic ? D.brandBord : D.borderMed,
                }}
                rows={3}
                placeholder="Diagnostic principal et différentiel…"
                value={form.diagnostic}
                onChange={e => setForm(f => ({ ...f, diagnostic: e.target.value }))}
              />
              {!form.diagnostic && (
                <div style={{ marginTop: 5, fontSize: 11, color: '#f59e0b', display: 'flex', alignItems: 'center', gap: 5 }}>
                  <Icon name="x" size={11} /> Requis pour terminer la consultation
                </div>
              )}
            </div>

            {/* Notes */}
            <div>
              <SectionLabel icon="edit">Notes & Recommandations</SectionLabel>
              <textarea
                style={{ ...inputStyle, resize: 'vertical', lineHeight: 1.6, minHeight: 80 }}
                rows={3}
                placeholder="Conduite thérapeutique, suivi, recommandations patient…"
                value={form.notes}
                onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              />
            </div>

            {/* Email notice */}
            <div style={{
              display: 'flex', alignItems: 'flex-start', gap: 10, padding: '11px 14px',
              background: D.cardAlt, borderRadius: 9, border: `1px solid ${D.border}`,
              fontSize: 12, color: D.textSec, lineHeight: 1.6,
            }}>
              <Icon name="mail" size={14} style={{ flexShrink: 0, marginTop: 1, color: D.brand }} />
              <span>
                En terminant, un <strong style={{ color: D.textPrim }}>compte-rendu PDF</strong> sera envoyé automatiquement à{' '}
                <strong style={{ color: D.brand }}>{appt?.patient_detail?.nom_complet}</strong>.
              </span>
            </div>
          </div>

          {/* ── Footer ── */}
          <div style={{
            padding: '12px 18px', borderTop: `1px solid ${D.border}`,
            background: D.card, display: 'flex', gap: 10, flexShrink: 0,
          }}>
            <button
              onClick={() => navigate('/appointments')}
              disabled={submitting}
              style={{
                flex: 1, padding: '10px 0', borderRadius: 8,
                background: D.cardAlt, border: `1px solid ${D.borderMed}`,
                color: D.textSec, fontWeight: 600, fontSize: 13, cursor: 'pointer',
                fontFamily: 'var(--font-sans)',
              }}
            >
              Annuler
            </button>
            <button
              onClick={handleSubmit}
              disabled={!form.diagnostic.trim() || submitting}
              style={{
                flex: 2, padding: '10px 0', borderRadius: 8, border: 'none',
                background: (!form.diagnostic.trim() || submitting) ? 'rgba(78,181,131,0.35)' : D.brand,
                color: '#ffffff', fontWeight: 700, fontSize: 13,
                cursor: (!form.diagnostic.trim() || submitting) ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
                fontFamily: 'var(--font-sans)', transition: 'background .15s',
              }}
            >
              {submitting
                ? <><span style={{ width: 13, height: 13, borderRadius: '50%', border: '2px solid rgba(255,255,255,0.4)', borderTopColor: '#ffffff', animation: 'spin 0.7s linear infinite', display: 'inline-block' }} /> Enregistrement…</>
                : <><Icon name="check" size={14} stroke={2.5} /> Terminer et envoyer le rapport</>
              }
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
