import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import { SkeletonTable } from '../components/Skeleton'
import ConfirmModal from '../components/ConfirmModal'
import { Calendar, List, Plus, Trash2, Video } from 'lucide-react'

const STATUS_COLORS = {
  planned:     'badge-amber',
  confirmed:   'badge-indigo',
  in_progress: 'badge-violet',
  completed:   'badge-emerald',
  cancelled:   'badge-rose',
}
const STATUS_LABELS = {
  planned: 'Planifié', confirmed: 'Confirmé',
  in_progress: 'En cours', completed: 'Terminé', cancelled: 'Annulé',
}

const EMPTY_FORM = {
  patient: '', doctor: '', scheduled_at: '',
  duration: 30, reason: '', status: 'planned', is_teleconsultation: false,
}

const inputClass = "input-base"
const labelClass = "label-xs mb-1.5 block"

/* ── Mini calendar week view ────────────────────────────────── */
function WeekView({ appointments }) {
  const today = new Date()
  // Build a 7-day window from previous Monday
  const dayOfWeek = today.getDay() === 0 ? 6 : today.getDay() - 1
  const monday = new Date(today); monday.setDate(today.getDate() - dayOfWeek)

  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday); d.setDate(monday.getDate() + i)
    return d
  })

  const byDay = (day) => appointments.filter(a => {
    const d = new Date(a.scheduled_at)
    return d.toDateString() === day.toDateString()
  })

  const dayNames = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

  return (
    <div className="overflow-x-auto soft-scrollbar">
      <div className="min-w-[640px] grid grid-cols-7 gap-2 p-5">
        {days.map((day, i) => {
          const isToday = day.toDateString() === today.toDateString()
          const appts = byDay(day)
          return (
            <div key={i} className={`rounded-2xl border ${isToday ? 'border-emerald-300 bg-emerald-50/60' : 'border-slate-100 bg-white/60'} p-2.5 min-h-[120px]`}>
              <div className="text-center mb-2">
                <p className="label-xs text-slate-400">{dayNames[i]}</p>
                <p className={`text-lg font-black mt-0.5 ${isToday ? 'text-emerald-600' : 'text-slate-800'}`}>{day.getDate()}</p>
              </div>
              <div className="space-y-1">
                {appts.map(a => (
                  <div key={a.id} className={`rounded-lg px-2 py-1 text-[10px] font-semibold leading-tight ${STATUS_COLORS[a.status] ? 'badge ' + STATUS_COLORS[a.status] : 'bg-slate-100 text-slate-600'}`}>
                    {new Date(a.scheduled_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })} — {a.patient_detail?.full_name?.split(' ')[0] || '?'}
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState([])
  const [patients, setPatients]   = useState([])
  const [doctors, setDoctors]     = useState([])
  const [view, setView]           = useState('list') // 'list' | 'week'
  const [showForm, setShowForm]   = useState(false)
  const [form, setForm]           = useState(EMPTY_FORM)
  const [filterDate, setFilterDate] = useState('')
  const [listLoading, setListLoading] = useState(true)
  const [saving, setSaving]       = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const fetchAll = useCallback(async () => {
    try {
      const params = filterDate ? `?date=${filterDate}` : ''
      const [appts, pts, users] = await Promise.all([
        api.get(`/api/appointments/${params}`),
        api.get('/api/patients/'),
        api.get('/api/users/doctors/'),
      ])
      setAppointments(appts.data.results || appts.data)
      setPatients(pts.data.results || pts.data)
      setDoctors((users.data.results || users.data).filter(u => u.role === 'doctor'))
    } catch {
      toast.error('Impossible de charger les rendez-vous.')
    }
  }, [filterDate])

  useEffect(() => {
    fetchAll().finally(() => setListLoading(false))
  }, [fetchAll])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/api/appointments/', form)
      setShowForm(false)
      setForm(EMPTY_FORM)
      await fetchAll()
      toast.success('Rendez-vous créé avec succès !')
    } catch (err) {
      const msg = err.response?.data?.non_field_errors?.[0] || 'Erreur lors de la création.'
      toast.error(msg)
    } finally {
      setSaving(false)
    }
  }

  const handleStatusChange = async (id, status) => {
    try {
      await api.patch(`/api/appointments/${id}/`, { status })
      setAppointments(prev => prev.map(a => a.id === id ? { ...a, status } : a))
    } catch {
      toast.error('Impossible de mettre à jour le statut.')
    }
  }

  const handleDelete = async (id) => {
    await api.delete(`/api/appointments/${id}/`)
    setAppointments(prev => prev.filter(a => a.id !== id))
    toast.success('Rendez-vous supprimé.')
  }

  const setField = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  return (
    <div className="p-5 md:p-6 space-y-5 max-w-[1400px]">

      {/* Header */}
      <section className="surface-panel rounded-3xl px-6 py-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="label-xs text-emerald-700">Planning médical</p>
            <h1 className="section-title mt-1.5 text-3xl font-black text-slate-900">Rendez-vous</h1>
            <p className="mt-1 text-sm text-slate-500">{appointments.length} rendez-vous</p>
          </div>
          <div className="flex flex-wrap items-center gap-2.5">
            {/* View toggle */}
            <div className="flex rounded-xl bg-slate-100 p-1 gap-1">
              {[['list', List, 'Liste'], ['week', Calendar, 'Semaine']].map((item) => {
                const [v, ViewIcon, label] = item
                return (
                <button
                  key={v}
                  onClick={() => setView(v)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    view === v ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  <ViewIcon size={13} />{label}
                </button>
              )})}
            </div>
            {/* Date filter */}
            <input
              type="date"
              value={filterDate}
              onChange={e => setFilterDate(e.target.value)}
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-100 focus:border-emerald-400 transition-all"
            />
            {filterDate && (
              <button
                onClick={() => setFilterDate('')}
                className="text-slate-400 hover:text-slate-600 transition-colors text-sm"
                title="Effacer le filtre"
              >
                ✕
              </button>
            )}
            <button onClick={() => setShowForm(true)} className="btn-primary">
              <Plus size={16} />
              Nouveau RDV
            </button>
          </div>
        </div>
      </section>

      {/* Content */}
      <div className="surface-panel rounded-3xl overflow-hidden">
        {listLoading ? (
          <SkeletonTable rows={5} cols={6} />
        ) : view === 'week' ? (
          <WeekView appointments={appointments} />
        ) : (
          <div className="overflow-x-auto soft-scrollbar">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  {['Patient', 'Médecin', 'Date & Heure', 'Durée', 'Type', 'Statut', ''].map(h => (
                    <th key={h} className="px-5 py-3.5 label-xs">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {appointments.map(a => (
                  <tr key={a.id} className="table-row-hover">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center text-xs font-bold text-emerald-700 shrink-0">
                          {a.patient_detail?.full_name?.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase() || '?'}
                        </div>
                        <p className="text-sm font-semibold text-slate-900">{a.patient_detail?.full_name || '—'}</p>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-600">
                      Dr. {a.doctor_detail?.last_name || '—'}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-700">
                      {new Date(a.scheduled_at).toLocaleString('fr-FR', {
                        day:'2-digit', month:'2-digit', year:'numeric',
                        hour:'2-digit', minute:'2-digit',
                      })}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">{a.duration} min</td>
                    <td className="px-5 py-3.5">
                      {a.is_teleconsultation ? (
                        <div className="flex flex-col gap-1">
                          <span className="badge badge-sky inline-flex items-center gap-1">
                            <Video size={11} />Vidéo
                          </span>
                          {a.teleconsultation_link?.includes('meet.jit.si/') && (
                            <Link
                              to={`/video?room=${a.teleconsultation_link.split('meet.jit.si/')[1]}`}
                              className="text-[10px] text-sky-500 hover:underline"
                            >
                              Rejoindre →
                            </Link>
                          )}
                        </div>
                      ) : (
                        <span className="badge badge-slate">Cabinet</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      <select
                        value={a.status}
                        onChange={e => handleStatusChange(a.id, e.target.value)}
                        className={`badge cursor-pointer focus:outline-none ${STATUS_COLORS[a.status] || 'badge-slate'}`}
                        onClick={e => e.stopPropagation()}
                      >
                        {Object.entries(STATUS_LABELS).map(([v, l]) => (
                          <option key={v} value={v}>{l}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-5 py-3.5">
                      <button
                        onClick={() => setConfirmDelete({ id: a.id, label: new Date(a.scheduled_at).toLocaleString('fr-FR', { day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' }) })}
                        className="w-8 h-8 rounded-xl bg-slate-100 hover:bg-rose-100 hover:text-rose-600 text-slate-400 flex items-center justify-center transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
                {appointments.length === 0 && (
                  <tr>
                    <td colSpan={7} className="py-16 text-center">
                      <div className="flex flex-col items-center gap-3 text-slate-400">
                        <Calendar size={32} className="opacity-30" />
                        <p className="text-sm font-medium">Aucun rendez-vous{filterDate ? ' pour cette date' : ''}</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Create modal ── */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-slate-950/40 backdrop-blur-sm">
          <div
            className="surface-panel-strong w-full max-w-lg rounded-3xl overflow-hidden"
            style={{ animation: 'confirmIn 0.3s cubic-bezier(0.16,1,0.3,1) both' }}
          >
            {/* Modal header */}
            <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
              <div>
                <p className="label-xs text-emerald-700">Planification</p>
                <h2 className="section-title text-xl font-black text-slate-900 mt-1">Nouveau rendez-vous</h2>
              </div>
              <button onClick={() => setShowForm(false)} className="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500 transition-colors">
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className={labelClass}>Patient</label>
                <select required value={form.patient} onChange={e => setField('patient', e.target.value)} className={inputClass}>
                  <option value="">Sélectionner un patient</option>
                  {patients.map(p => <option key={p.id} value={p.id}>{p.full_name}</option>)}
                </select>
              </div>
              <div>
                <label className={labelClass}>Médecin</label>
                <select required value={form.doctor} onChange={e => setField('doctor', e.target.value)} className={inputClass}>
                  <option value="">Sélectionner un médecin</option>
                  {doctors.map(d => <option key={d.id} value={d.id}>Dr. {d.last_name} {d.first_name}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={labelClass}>Date et heure</label>
                  <input type="datetime-local" required value={form.scheduled_at} onChange={e => setField('scheduled_at', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Durée (min)</label>
                  <input type="number" min={15} max={120} value={form.duration} onChange={e => setField('duration', e.target.value)} className={inputClass} />
                </div>
              </div>
              <div>
                <label className={labelClass}>Motif de consultation</label>
                <input type="text" required value={form.reason} onChange={e => setField('reason', e.target.value)} placeholder="Ex: Consultation de routine" className={inputClass} />
              </div>

              {/* Teleconsultation toggle */}
              <label className="flex items-center gap-3 rounded-xl border border-slate-200 p-4 cursor-pointer hover:bg-slate-50 transition-colors">
                <input
                  type="checkbox"
                  checked={form.is_teleconsultation}
                  onChange={e => setField('is_teleconsultation', e.target.checked)}
                  className="w-4 h-4 accent-emerald-500 rounded"
                />
                <div className="flex items-center gap-2">
                  <Video size={16} className="text-sky-500" />
                  <span className="text-sm font-semibold text-slate-700">Téléconsultation</span>
                </div>
                <span className="ml-auto text-xs text-slate-400">Lien généré automatiquement</span>
              </label>

              <div className="flex gap-3 pt-1">
                <button type="button" onClick={() => setShowForm(false)} className="btn-ghost flex-1">Annuler</button>
                <button type="submit" disabled={saving} className="btn-primary flex-1 justify-center">
                  {saving ? 'Enregistrement…' : 'Créer le RDV'}
                </button>
              </div>
            </form>
          </div>

          {/* Inline keyframe for modal */}
          <style>{`@keyframes confirmIn { from{opacity:0;transform:scale(0.95) translateY(12px)} to{opacity:1;transform:scale(1) translateY(0)} }`}</style>
        </div>
      )}

      {/* ── Confirm delete ── */}
      {confirmDelete && (
        <ConfirmModal
          title="Supprimer le rendez-vous ?"
          message={`Le rendez-vous du ${confirmDelete.label} sera définitivement supprimé.`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onClose={() => setConfirmDelete(null)}
        />
      )}
    </div>
  )
}