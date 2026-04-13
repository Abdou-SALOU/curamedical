import { useEffect, useMemo, useState, useCallback } from 'react'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import ConfirmModal from '../components/ConfirmModal'
import { SkeletonTable } from '../components/Skeleton'
import { FilePlus, Brain, AlertTriangle, Activity, Sparkles, Trash2 } from 'lucide-react'

const SYMPTOMS = [
  { value: 'fever',                    label: 'Fièvre',                   hint: 'Température élevée ou frissons.' },
  { value: 'high_fever',               label: 'Fièvre élevée',            hint: 'Température > 39°C, état clinique sévère.' },
  { value: 'mild_fever',               label: 'Fièvre légère',            hint: 'Température 37.5–38.5°C.' },
  { value: 'chills',                   label: 'Frissons',                  hint: 'Sensations de froid intenses.' },
  { value: 'sweating',                 label: 'Transpiration excessive',   hint: 'Sueurs nocturnes ou diurnes.' },
  { value: 'fatigue',                  label: 'Fatigue / Asthénie',        hint: 'Épuisement inhabituel.' },
  { value: 'lethargy',                 label: 'Léthargie',                 hint: 'Manque d\'énergie, somnolence.' },
  { value: 'cough',                    label: 'Toux',                      hint: 'Toux sèche ou grasse.' },
  { value: 'breathlessness',           label: 'Difficulté respiratoire',   hint: 'Essoufflement ou dyspnée.' },
  { value: 'chest_pain',               label: 'Douleur thoracique',        hint: 'Oppression ou douleur poitrine.' },
  { value: 'headache',                 label: 'Maux de tête',              hint: 'Céphalées, migraines.' },
  { value: 'dizziness',                label: 'Vertiges',                  hint: 'Sensation de tournis ou d\'instabilité.' },
  { value: 'nausea',                   label: 'Nausées',                   hint: 'Envie de vomir sans vomissement.' },
  { value: 'vomiting',                 label: 'Vomissements',              hint: 'Vomissements actifs.' },
  { value: 'diarrhoea',                label: 'Diarrhée',                  hint: 'Selles liquides fréquentes.' },
  { value: 'abdominal_pain',           label: 'Douleur abdominale',        hint: 'Crampes ou douleurs au ventre.' },
  { value: 'stomach_pain',             label: 'Douleur gastrique',         hint: 'Douleurs à l\'estomac, brûlures.' },
  { value: 'constipation',             label: 'Constipation',              hint: 'Difficultés à aller à la selle.' },
  { value: 'indigestion',              label: 'Indigestion',               hint: 'Digestion difficile après les repas.' },
  { value: 'back_pain',                label: 'Douleur dorsale',           hint: 'Douleurs lombaires ou dorsales.' },
  { value: 'joint_pain',               label: 'Douleurs articulaires',     hint: 'Douleurs dans les articulations.' },
  { value: 'muscle_pain',              label: 'Douleurs musculaires',      hint: 'Myalgie, courbatures.' },
  { value: 'neck_stiffness',           label: 'Raideur de nuque',          hint: 'Difficulté à tourner la tête.' },
  { value: 'skin_rash',                label: 'Éruption cutanée',          hint: 'Rougeurs, boutons, plaques.' },
  { value: 'itching',                  label: 'Démangeaisons',             hint: 'Prurit généralisé ou localisé.' },
  { value: 'yellowish_skin',           label: 'Teinte jaune (Jaunisse)',   hint: 'Ictère cutané ou oculaire.' },
  { value: 'dark_urine',               label: 'Urines foncées',            hint: 'Urines marrons ou très foncées.' },
  { value: 'weight_loss',              label: 'Perte de poids',            hint: 'Amaigrissement inexpliqué.' },
  { value: 'loss_of_appetite',         label: 'Perte d\'appétit',         hint: 'Anorexie ou refus de s\'alimenter.' },
  { value: 'swollen_lymph_nodes',      label: 'Ganglions gonflés',         hint: 'Adénopathie cervicale ou axillaire.' },
  { value: 'runny_nose',               label: 'Écoulement nasal',          hint: 'Rhinorrhée, rhume.' },
  { value: 'throat_irritation',        label: 'Irritation de la gorge',    hint: 'Pharyngite, mal de gorge.' },
  { value: 'redness_of_eyes',          label: 'Yeux rouges',              hint: 'Conjonctivite ou irritation oculaire.' },
  { value: 'burning_micturition',      label: 'Brûlure à la miction',      hint: 'Douleur en urinant.' },
  { value: 'fast_heart_rate',          label: 'Palpitations / Tachycardie',hint: 'Cœur qui bat trop vite.' },
]

const EMPTY_FORM = {
  appointment: '', symptoms: [], clinical_exam: '',
  diagnosis: '', notes: '', ia_suggestions: null, ia_used: false,
}

const EMPTY_IA_PARAMS = { age: 30, gender: 'M', blood_pressure: 'Normal', cholesterol: 'Normal' }

const inputClass =
  'w-full rounded-2xl border border-slate-200/80 bg-white px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-emerald-300 focus:outline-none focus:ring-4 focus:ring-emerald-100'
const labelClass = 'mb-2 block text-[11px] font-bold uppercase tracking-[0.2em] text-slate-500'

export default function ConsultationsPage() {
  const [consultations, setConsultations] = useState([])
  const [appointments, setAppointments] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [iaParams, setIaParams] = useState(EMPTY_IA_PARAMS)
  const [loading, setLoading] = useState(false)
  const [listLoading, setListLoading] = useState(true)
  const [iaLoading, setIaLoading] = useState(false)
  const [iaSuggestions, setIaSuggestions] = useState(null)
  const [iaError, setIaError] = useState('')
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const fetchAll = useCallback(async () => {
    try {
      const [consults, appts] = await Promise.all([api.get('/api/consultations/'), api.get('/api/appointments/')])
      setConsultations(consults.data.results || consults.data)
      setAppointments(appts.data.results || appts.data)
    } catch {
      toast.error('Impossible de charger les consultations.')
    }
  }, [])

  useEffect(() => { fetchAll().finally(() => setListLoading(false)) }, [fetchAll])

  const availableAppointments = useMemo(() => {
    const usedIds = new Set(consultations.map(c => c.appointment))
    return appointments.filter(a => !usedIds.has(a.id))
  }, [appointments, consultations])

  const applyAppointmentDefaults = (appointmentId) => {
    setForm(prev => ({ ...prev, appointment: appointmentId }))
    const appt = appointments.find(a => String(a.id) === String(appointmentId))
    if (!appt?.patient_detail) return
    setIaParams(prev => ({ ...prev, age: appt.patient_detail.age || prev.age, gender: appt.patient_detail.gender || prev.gender }))
  }

  const toggleSymptom = (symptom) => {
    setIaSuggestions(null)
    setForm(prev => ({
      ...prev,
      symptoms: prev.symptoms.includes(symptom)
        ? prev.symptoms.filter(s => s !== symptom)
        : [...prev.symptoms, symptom],
    }))
  }

  const handleAskIA = async () => {
    if (form.symptoms.length === 0) {
      setIaError('Sélectionnez au moins un symptôme avant de lancer l\'analyse.')
      return
    }
    setIaLoading(true)
    setIaError('')
    setIaSuggestions(null)
    try {
      const { data } = await api.post('/api/consultations/ia/suggest/', {
        symptoms: form.symptoms,
        age: iaParams.age,
        gender: iaParams.gender,
        blood_pressure: iaParams.blood_pressure,
        cholesterol: iaParams.cholesterol,
      })

      // Le service peut retourner un tableau vide si aucune maladie n'est détectée
      const suggestions = data.suggestions || []
      setIaSuggestions(suggestions)
      // Auto-remplissage du diagnostic avec la suggestion la plus probable
      const topDiagnosis = suggestions.length > 0 ? suggestions[0].disease : ''
      setForm(prev => ({
        ...prev,
        ia_suggestions: suggestions,
        ia_used: suggestions.length > 0,
        diagnosis: topDiagnosis || prev.diagnosis,
      }))

      if (suggestions.length === 0) {
        setIaError('L\'IA n\'a pas pu produire de suggestion avec ces paramètres. Essayez d\'autres symptômes.')
      }
    } catch (err) {
      const detail =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        (err.response?.status === 503 ? 'Le service IA est temporairement indisponible (timeout ou non démarré).' : null) ||
        'Erreur inattendue lors de l\'appel à l\'IA.'
      setIaError(detail)
      setIaSuggestions([])
    } finally {
      setIaLoading(false)
    }
  }

  const closeForm = () => {
    setShowForm(false)
    setForm(EMPTY_FORM)
    setIaParams(EMPTY_IA_PARAMS)
    setIaSuggestions(null)
    setIaError('')
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.post('/api/consultations/', {
        appointment: parseInt(form.appointment, 10),
        symptoms: form.symptoms,
        clinical_exam: form.clinical_exam,
        diagnosis: form.diagnosis,
        notes: form.notes,
        ia_suggestions: form.ia_suggestions,
        ia_used: form.ia_used,
      })
      closeForm()
      fetchAll()
      toast.success('Consultation enregistrée avec succès !')
    } catch (err) {
      const detail = err.response?.data
      if (typeof detail === 'object') {
        const firstKey = Object.keys(detail)[0]
        setError(firstKey ? `${firstKey} : ${detail[firstKey]}` : 'Erreur lors de la création.')
      } else {
        setError('Erreur lors de la création.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    await api.delete(`/api/consultations/${id}/`)
    fetchAll()
    if (selected?.id === id) setSelected(null)
    toast.success('Consultation supprimée.')
  }

  return (
    <div className="p-6 space-y-5 min-h-screen">

      {/* Header */}
      <section className="surface-panel rounded-3xl px-6 py-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.24em] text-emerald-700">Suivi clinique</p>
            <h1 className="section-title mt-1 text-3xl font-black text-slate-900">Consultations médicales</h1>
            <p className="mt-1.5 text-sm text-slate-500 max-w-xl">
              Structurez l&apos;examen clinique, capturez les symptômes et exploitez l&apos;aide IA pour accélérer la prise de décision.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <div className="rounded-2xl bg-emerald-50 px-4 py-2.5 text-sm font-semibold text-emerald-700 border border-emerald-100">
              {consultations.length} consultation(s)
            </div>
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 px-5 py-2.5 font-semibold text-white text-sm shadow-[0_8px_24px_rgba(16,185,129,0.3)] transition-all hover:-translate-y-0.5"
            >
              <FilePlus size={17} />
              Nouvelle consultation
            </button>
          </div>
        </div>
      </section>

      {/* Content grid */}
      <section className="grid gap-5 lg:grid-cols-[1fr_380px]">

        {/* Table */}
        <div className="surface-panel rounded-3xl overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100/80">
            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-400">Historique</p>
            <h2 className="section-title mt-0.5 text-xl font-black text-slate-900">Dernières consultations</h2>
          </div>
          {listLoading ? (
            <SkeletonTable rows={5} cols={5} />
          ) : (
          <div className="overflow-x-auto soft-scrollbar">
            <table className="w-full text-left">
              <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
                <tr>
                  <th className="px-5 py-3.5">Patient</th>
                  <th className="px-5 py-3.5">Médecin</th>
                  <th className="px-5 py-3.5">Diagnostic</th>
                  <th className="px-5 py-3.5">IA</th>
                  <th className="px-5 py-3.5">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {consultations.map(c => (
                  <tr
                    key={c.id}
                    onClick={() => setSelected(c)}
                    className={`cursor-pointer transition-colors hover:bg-emerald-50/50 ${selected?.id === c.id ? 'bg-emerald-50/70' : ''}`}
                  >
                    <td className="px-5 py-3.5 font-semibold text-slate-900 text-sm">{c.patient_name || '—'}</td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">
                      {c.appointment_detail?.doctor_detail?.last_name ? `Dr. ${c.appointment_detail.doctor_detail.last_name}` : '—'}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-700 max-w-[180px] truncate">{c.diagnosis}</td>
                    <td className="px-5 py-3.5">
                      {c.ia_used
                        ? <span className="badge badge-emerald">IA consultée</span>
                        : <span className="text-xs text-slate-400">—</span>}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">{new Date(c.created_at).toLocaleDateString('fr-FR')}</td>
                  </tr>
                ))}
                {consultations.length === 0 && (
                  <tr><td colSpan={5} className="px-5 py-14 text-center text-sm text-slate-400">Aucune consultation enregistrée</td></tr>
                )}
              </tbody>
            </table>
          </div>
          )}
        </div>

        {/* Detail panel */}
        <aside className="surface-panel rounded-3xl p-5 overflow-y-auto soft-scrollbar max-h-[calc(100vh-220px)]">
          {selected ? (
            <div className="space-y-5">
              <div>
                <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-400">Dossier clinique</p>
                <h2 className="section-title mt-1 text-xl font-black text-slate-900">{selected.patient_name || 'Consultation'}</h2>
                <p className="text-sm text-slate-500 mt-1">
                  {selected.appointment_detail?.doctor_detail?.last_name ? `Dr. ${selected.appointment_detail.doctor_detail.last_name}` : 'Médecin non renseigné'}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-2xl bg-slate-50 p-3.5">
                  <p className="label-xs text-slate-400">Diagnostic</p>
                  <p className="mt-1.5 font-bold text-slate-900 text-sm">{selected.diagnosis}</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-3.5">
                  <p className="label-xs text-slate-400">Date</p>
                  <p className="mt-1.5 font-bold text-slate-900 text-sm">{new Date(selected.created_at).toLocaleDateString('fr-FR')}</p>
                </div>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <div className="flex items-center gap-2 text-sm font-bold text-slate-800 mb-3">
                  <Activity size={15} className="text-emerald-600" />
                  Symptômes observés
                </div>
                <div className="flex flex-wrap gap-2">
                  {(selected.symptoms || []).map(s => (
                    <span key={s} className="badge badge-emerald">{s.replace(/_/g, ' ')}</span>
                  ))}
                  {(!selected.symptoms || selected.symptoms.length === 0) && <span className="text-sm text-slate-400">Aucun symptôme saisi.</span>}
                </div>
              </div>

              <div className="space-y-3 text-sm">
                <div>
                  <p className="label-xs text-slate-400 mb-1.5">Examen clinique</p>
                  <p className="text-slate-700 leading-6">{selected.clinical_exam || 'Non renseigné.'}</p>
                </div>
                <div>
                  <p className="label-xs text-slate-400 mb-1.5">Notes</p>
                  <p className="text-slate-700 leading-6">{selected.notes || 'Aucune note complémentaire.'}</p>
                </div>
              </div>

              {selected.ia_suggestions?.length > 0 && (
                <div className="rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100 p-4">
                  <div className="flex items-center gap-2 text-sm font-bold text-slate-800 mb-3">
                    <Sparkles size={15} className="text-emerald-600" />
                    Suggestions IA
                  </div>
                  <div className="space-y-2">
                    {selected.ia_suggestions.map((s, i) => (
                      <div key={`${s.disease}-${i}`} className="rounded-xl bg-white/80 px-3.5 py-3">
                        <div className="flex items-center justify-between gap-3">
                          <p className="font-bold text-slate-900 text-sm">{s.disease}</p>
                          <span className="text-sm font-black text-emerald-700">{s.confidence}%</span>
                        </div>
                        {s.explanation && <p className="mt-1 text-xs text-slate-500 leading-5">{s.explanation}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button
                onClick={() => setConfirmDelete({ id: selected.id, name: selected.patient_name })}
                className="flex w-full items-center justify-center gap-2 rounded-2xl bg-rose-500/10 px-4 py-3 font-semibold text-rose-700 transition-colors hover:bg-rose-500/15 mt-4"
              >
                <Trash2 size={16} />
                Supprimer la consultation
              </button>
            </div>
          ) : (
            <div className="flex h-full min-h-[280px] flex-col items-center justify-center text-center px-4">
              <div className="w-14 h-14 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600 mb-4">
                <Brain size={24} />
              </div>
              <h2 className="section-title text-xl font-black text-slate-900">Sélectionnez une consultation</h2>
              <p className="mt-2 text-sm text-slate-400 leading-6 max-w-[240px]">
                Le panneau affiche le diagnostic, les symptômes et les suggestions IA.
              </p>
            </div>
          )}
        </aside>
      </section>

      {/* ── MODAL ── */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <div className="surface-panel-strong soft-scrollbar max-h-[92vh] w-full max-w-5xl overflow-y-auto rounded-[2rem] p-8">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="label-xs text-emerald-700">Nouvelle consultation</p>
                <h2 className="section-title mt-1.5 text-2xl font-black text-slate-900">Rédiger un compte rendu clinique</h2>
              </div>
              <button onClick={() => { setShowForm(false); setIaSuggestions(null) }} className="rounded-full bg-slate-100 p-2 text-slate-500 hover:bg-slate-200 transition-colors">
                <span className="material-symbols-outlined text-lg">close</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="grid gap-6 xl:grid-cols-2">
              {/* Left column */}
              <div className="space-y-5">
                <div>
                  <label className={labelClass}>Rendez-vous associé</label>
                  <select required value={form.appointment} onChange={e => applyAppointmentDefaults(e.target.value)} className={inputClass}>
                    <option value="">Sélectionner un rendez-vous</option>
                    {availableAppointments.map(a => (
                      <option key={a.id} value={a.id}>
                        {a.patient_detail?.full_name} — {new Date(a.scheduled_at).toLocaleString('fr-FR', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className={labelClass}>Symptômes observés</label>
                  <div className="grid grid-cols-2 gap-3">
                    {SYMPTOMS.map(s => {
                      const active = form.symptoms.includes(s.value)
                      return (
                        <button
                          key={s.value} type="button" onClick={() => toggleSymptom(s.value)}
                          className={`rounded-2xl border px-4 py-3.5 text-left transition-all ${active ? 'border-emerald-300 bg-emerald-50 shadow-[0_6px_20px_rgba(16,185,129,0.12)]' : 'border-slate-200 bg-white hover:border-emerald-200 hover:bg-emerald-50/40'}`}
                        >
                          <p className="font-bold text-sm text-slate-900">{s.label}</p>
                          <p className="mt-0.5 text-xs text-slate-500 leading-5">{s.hint}</p>
                        </button>
                      )
                    })}
                  </div>
                </div>

                <div>
                  <label className={labelClass}>Examen clinique</label>
                  <textarea rows={4} value={form.clinical_exam} onChange={e => setForm({ ...form, clinical_exam: e.target.value })} className={`${inputClass} resize-none`} />
                </div>
                <div>
                  <label className={labelClass}>Diagnostic retenu</label>
                  <input type="text" required value={form.diagnosis} onChange={e => setForm({ ...form, diagnosis: e.target.value })} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Notes complémentaires</label>
                  <textarea rows={3} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} className={`${inputClass} resize-none`} />
                </div>
              </div>

              {/* Right column — IA */}
              <div className="space-y-5">
                <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-emerald-950 p-5 text-white">
                  <div className="flex items-center justify-between gap-3 mb-5">
                    <div>
                      <p className="label-xs text-emerald-300/80">Assistant IA</p>
                      <h3 className="mt-1.5 text-xl font-black">Analyse contextuelle</h3>
                    </div>
                    <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                      <Brain size={20} />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="mb-2 block text-[11px] font-bold uppercase tracking-[0.2em] text-emerald-100/70">Âge</label>
                      <input type="number" min={1} max={120} value={iaParams.age} onChange={e => setIaParams({ ...iaParams, age: parseInt(e.target.value || '0', 10) })} className="w-full rounded-xl border border-white/10 bg-white/10 px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-400/30" />
                    </div>
                    <div>
                      <label className="mb-2 block text-[11px] font-bold uppercase tracking-[0.2em] text-emerald-100/70">Genre</label>
                      <select value={iaParams.gender} onChange={e => setIaParams({ ...iaParams, gender: e.target.value })} className="w-full rounded-xl border border-white/10 bg-white/10 px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-400/30">
                        <option value="M" className="text-slate-900">Masculin</option>
                        <option value="F" className="text-slate-900">Féminin</option>
                      </select>
                    </div>
                    <div>
                      <label className="mb-2 block text-[11px] font-bold uppercase tracking-[0.2em] text-emerald-100/70">Pression art.</label>
                      <select value={iaParams.blood_pressure} onChange={e => setIaParams({ ...iaParams, blood_pressure: e.target.value })} className="w-full rounded-xl border border-white/10 bg-white/10 px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-400/30">
                        <option value="Low" className="text-slate-900">Basse</option>
                        <option value="Normal" className="text-slate-900">Normale</option>
                        <option value="High" className="text-slate-900">Haute</option>
                      </select>
                    </div>
                    <div>
                      <label className="mb-2 block text-[11px] font-bold uppercase tracking-[0.2em] text-emerald-100/70">Cholestérol</label>
                      <select value={iaParams.cholesterol} onChange={e => setIaParams({ ...iaParams, cholesterol: e.target.value })} className="w-full rounded-xl border border-white/10 bg-white/10 px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-400/30">
                        <option value="Low" className="text-slate-900">Bas</option>
                        <option value="Normal" className="text-slate-900">Normal</option>
                        <option value="High" className="text-slate-900">Élevé</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-4 flex items-start gap-2.5 rounded-xl bg-amber-300/10 border border-amber-300/20 px-3.5 py-3 text-xs text-amber-200/90 leading-5">
                    <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                    Outil d&apos;aide à la décision. Le diagnostic final reste médical et humain.
                  </div>

                  <button
                    type="button" onClick={handleAskIA} disabled={iaLoading || form.symptoms.length === 0}
                    className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-400 px-4 py-3 text-sm font-bold text-slate-950 transition-all hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {iaLoading ? <span className="h-4 w-4 rounded-full border-2 border-slate-950/20 border-t-slate-950 animate-spin" /> : <><Sparkles size={15} />Lancer l&apos;analyse IA</>}
                  </button>
                </div>

                {iaError && <div className="rounded-2xl bg-rose-50 border border-rose-100 px-4 py-3 text-sm text-rose-700">{iaError}</div>}

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="label-xs text-slate-400 mb-3">Résultats IA</p>
                  {iaSuggestions?.length > 0 ? (
                    <div className="space-y-2">
                      {iaSuggestions.map((s, i) => (
                        <button
                          key={`${s.disease}-${i}`} type="button"
                          onClick={() => setForm(prev => ({ ...prev, diagnosis: s.disease }))}
                          className="w-full rounded-xl bg-white px-4 py-3 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
                        >
                          <div className="flex items-center justify-between gap-3">
                            <p className="font-bold text-sm text-slate-900">{s.disease}</p>
                            <span className="text-sm font-black text-emerald-700">{s.confidence}%</span>
                          </div>
                          {s.explanation && <p className="mt-1 text-xs text-slate-500 leading-5">{s.explanation}</p>}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-400 leading-6">Lancez une analyse pour obtenir des hypothèses et un niveau de confiance.</p>
                  )}
                </div>
              </div>

              {error && <div className="xl:col-span-2 rounded-2xl bg-rose-50 border border-rose-100 px-4 py-3 text-sm text-rose-700">{error}</div>}

              <div className="xl:col-span-2 flex justify-end gap-3 pt-1">
                <button type="button" onClick={() => { setShowForm(false); setIaSuggestions(null) }} className="rounded-2xl bg-slate-100 px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-200 transition-colors">
                  Annuler
                </button>
                <button type="submit" disabled={loading} className="rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 px-5 py-2.5 text-sm font-semibold text-white shadow-[0_8px_24px_rgba(16,185,129,0.3)] hover:-translate-y-0.5 transition-all disabled:opacity-60">
                  {loading ? 'Enregistrement...' : 'Enregistrer la consultation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirmDelete && (
        <ConfirmModal
          title="Supprimer la consultation ?"
          message={`La consultation de ${confirmDelete.name} sera définitivement supprimée.`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onClose={() => setConfirmDelete(null)}
        />
      )}
    </div>
  )
}
