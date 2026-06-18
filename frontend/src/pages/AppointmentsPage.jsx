import { useEffect, useState, useCallback } from 'react'
import { Link, useLocation } from 'react-router-dom'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import { SkeletonTable } from '../components/Skeleton'
import ConfirmModal from '../components/ConfirmModal'
import Pagination from '../components/Pagination'
import { Calendar, CalendarDays, List, Plus, RotateCcw, Trash2, Video } from 'lucide-react'

const PAGE_SIZE = 10

const STATUS_COLORS = {
  DEMANDE:  'badge-sky',
  PLANIFIE: 'badge-amber',
  CONFIRME: 'badge-indigo',
  EN_COURS: 'badge-violet',
  TERMINE:  'badge-emerald',
  ANNULE:   'badge-rose',
}
const STATUS_LABELS = {
  DEMANDE:  'En attente',
  PLANIFIE: 'Planifié',
  CONFIRME: 'Confirmé',
  EN_COURS: 'En cours',
  TERMINE:  'Terminé',
  ANNULE:   'Annulé',
}

const STATUS_HEX_COLORS = {
  DEMANDE:  '#64748b',
  PLANIFIE: '#f59e0b',
  CONFIRME: '#2563eb',
  EN_COURS: '#8b5cf6',
  TERMINE:  '#10b981',
  ANNULE:   '#ef4444',
}

const EMPTY_FORM = {
  patient: '', medecin: '', date_heure: '',
  duree: 30, motif: '', statut: 'PLANIFIE', type_consultation: 'PRESENTIEL',
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
    const d = new Date(a.date_heure)
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
                  <div key={a.id} className={`rounded-lg px-2 py-1 text-[10px] font-semibold leading-tight ${STATUS_COLORS[a.statut] ? 'badge ' + STATUS_COLORS[a.statut] : 'bg-slate-100 text-slate-600'}`}>
                    {new Date(a.date_heure).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })} — {a.patient_nom?.split(' ')[0] || '?'}
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

function CalendarView({ appointments }) {
  const events = appointments
    .filter(a => a.date_heure)
    .map(a => {
      const start = new Date(a.date_heure)
      const duration = Number(a.duree || 30)
      const end = new Date(start.getTime() + duration * 60000)
      const patientName = a.patient_detail?.nom_complet || a.patient_nom || 'Patient'
      const motif = a.motif || 'Consultation'

      return {
        id: String(a.id),
        title: `${patientName} - ${motif}`,
        start: start.toISOString(),
        end: end.toISOString(),
        backgroundColor: STATUS_HEX_COLORS[a.statut] || STATUS_HEX_COLORS.PLANIFIE,
        borderColor: 'transparent',
        extendedProps: a,
      }
    })

  return (
    <div className="p-4 md:p-5">
      <style>{`
        .curamedical-calendar .fc { font-family: Inter, system-ui, sans-serif; }
        .curamedical-calendar .fc-toolbar-title { font-size: 1.05rem; font-weight: 900; color: #0f172a; }
        .curamedical-calendar .fc-button-primary {
          background: #059669 !important;
          border: 0 !important;
          border-radius: 10px !important;
          box-shadow: none !important;
          font-size: 12px !important;
          font-weight: 800 !important;
          text-transform: capitalize !important;
        }
        .curamedical-calendar .fc-button-primary:hover { background: #047857 !important; }
        .curamedical-calendar .fc-button-active { background: #064e3b !important; }
        .curamedical-calendar .fc-event {
          border-radius: 9px;
          padding: 2px 5px;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
        }
        .curamedical-calendar .fc-col-header-cell {
          padding: 10px 0;
          background: #f8fafc;
          color: #64748b;
          font-size: 11px;
          font-weight: 900;
          text-transform: uppercase;
        }
        .curamedical-calendar .fc-theme-standard td,
        .curamedical-calendar .fc-theme-standard th { border-color: #e2e8f0; }
        .curamedical-calendar .fc-timegrid-slot { height: 42px !important; }
      `}</style>
      <div className="curamedical-calendar min-h-[650px]">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay',
          }}
          events={events}
          height="650px"
          slotMinTime="08:00:00"
          slotMaxTime="20:00:00"
          allDaySlot={false}
          locale="fr"
          firstDay={1}
          nowIndicator
          buttonText={{ today: "Aujourd'hui", month: 'Mois', week: 'Semaine', day: 'Jour' }}
          eventClick={(info) => {
            const r = info.event.extendedProps
            toast.info(`${r.patient_detail?.nom_complet || r.patient_nom || 'Patient'} - ${STATUS_LABELS[r.statut] || r.statut}`)
          }}
        />
      </div>
    </div>
  )
}

export default function AppointmentsPage() {
  const location = useLocation()
  const urlParams = new URLSearchParams(location.search)
  const initType = urlParams.get('type') || ''

  const [appointments, setAppointments] = useState([])
  const [count, setCount]         = useState(0)
  const [page, setPage]           = useState(1)
  const [patients, setPatients]   = useState([])
  const [doctors, setDoctors]     = useState([])
  const [view, setView]           = useState('list') // 'list' | 'week' | 'calendar'
  const [showForm, setShowForm]   = useState(false)
  const [form, setForm]           = useState(EMPTY_FORM)
  const [filterDate, setFilterDate] = useState('')
  const [filterType, setFilterType] = useState(initType)
  const [listLoading, setListLoading] = useState(true)
  const [saving, setSaving]       = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [showTrash, setShowTrash]         = useState(false)
  const [trashItems, setTrashItems]       = useState([])
  const [trashLoading, setTrashLoading]   = useState(false)

  const fetchTrash = async () => {
    setTrashLoading(true)
    try {
      const { data } = await api.get('/api/appointments/corbeille/')
      setTrashItems(data.results || data)
    } catch { toast.error('Impossible de charger la corbeille.') }
    finally { setTrashLoading(false) }
  }

  const handleRestore = async (id) => {
    try {
      await api.post(`/api/appointments/${id}/restaurer/`)
      setTrashItems(prev => prev.filter(a => a.id !== id))
      await fetchAll()
      toast.success('Rendez-vous restauré.')
    } catch { toast.error('Impossible de restaurer le rendez-vous.') }
  }

  const handleDeleteForever = async (id) => {
    try {
      await api.delete(`/api/appointments/${id}/supprimer-definitif/`)
      setTrashItems(prev => prev.filter(a => a.id !== id))
      toast.success('Supprimé définitivement.')
    } catch { toast.error('Impossible de supprimer définitivement.') }
  }

  const fetchAll = useCallback(async () => {
    const dateParam = filterDate ? `&date=${filterDate}` : ''
    // Vue liste : pagination serveur. Vues semaine/calendrier : période complète.
    const apptQuery = view === 'list'
      ? `?page_size=${PAGE_SIZE}&page=${page}${dateParam}`
      : `?page_size=500${dateParam}`
    const [appts, pts, users] = await Promise.allSettled([
      api.get(`/api/appointments/${apptQuery}`),
      api.get('/api/patients/?page_size=500'),
      api.get('/api/users/medecins/'),
    ])
    if (appts.status === 'fulfilled') {
      const results = appts.value.data.results || appts.value.data
      setAppointments(results)
      setCount(appts.value.data.count ?? results.length)
    } else {
      toast.error('Impossible de charger les rendez-vous.')
    }
    if (pts.status === 'fulfilled') {
      setPatients(pts.value.data.results || pts.value.data)
    }
    if (users.status === 'fulfilled') {
      setDoctors((users.value.data.results || users.value.data).filter(u => u.role === 'medecin'))
    }
  }, [filterDate, view, page])

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

  const handleStatusChange = async (id, statut) => {
    try {
      await api.patch(`/api/appointments/${id}/update-statut/`, { statut })
      setAppointments(prev => prev.map(a => a.id === id ? { ...a, statut } : a))
    } catch {
      toast.error('Impossible de mettre à jour le statut.')
    }
  }

  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/appointments/${id}/`)
      await fetchAll()
      toast.success('Déplacé dans la corbeille.')
    } catch {
      toast.error('Impossible de supprimer ce rendez-vous.')
    }
  }

  const setField = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  return (
    <div className="cm-page">

      {/* Header */}
      <section className="cm-card cm-mb-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="cm-eyebrow">Planning médical</div>
            <div className="cm-title">Rendez-vous</div>
            <div className="cm-sub">{count} rendez-vous</div>
          </div>
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Type filter */}
            <div className="flex rounded-xl bg-slate-100 p-1 gap-1">
              {[['', 'Tous'], ['EN_LIGNE', '📹 Téléconsultations'], ['PRESENTIEL', '🏥 Cabinet']].map(([v, l]) => (
                <button key={v} onClick={() => setFilterType(v)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${filterType === v ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}>
                  {l}
                </button>
              ))}
            </div>
            {/* View toggle */}
            <div className="flex rounded-xl bg-slate-100 p-1 gap-1">
              {[['list', List, 'Liste'], ['week', Calendar, 'Semaine'], ['calendar', CalendarDays, 'Calendrier']].map((item) => {
                const [v, ViewIcon, label] = item
                return (
                <button
                  key={v}
                  onClick={() => { setView(v); setPage(1) }}
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
              onChange={e => { setFilterDate(e.target.value); setPage(1) }}
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
            <button onClick={() => { setShowTrash(true); fetchTrash() }} className="cm-btn cm-btn-ghost" title="Corbeille">
              <Trash2 size={15} /> Corbeille
            </button>
            <button onClick={() => setShowForm(true)} className="cm-btn cm-btn-brand">
              <Plus size={16} />
              Nouveau RDV
            </button>
          </div>
        </div>
      </section>

      {/* Content */}
      <div className="cm-card" style={{ padding: 0, overflow: 'hidden' }}>
        {listLoading ? (
          <SkeletonTable rows={5} cols={6} />
        ) : view === 'week' ? (
          <WeekView appointments={appointments} />
        ) : view === 'calendar' ? (
          <CalendarView appointments={appointments} />
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
                {appointments.filter(a => !filterType || a.type_consultation === filterType).map(a => (
                  <tr key={a.id} className="table-row-hover">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center text-xs font-bold text-emerald-700 shrink-0">
                          {a.patient_nom?.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase() || '?'}
                        </div>
                        <p className="text-sm font-semibold text-slate-900">{a.patient_nom || '—'}</p>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-600">
                      {a.medecin_nom || '—'}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-700">
                      {new Date(a.date_heure).toLocaleString('fr-FR', {
                        day:'2-digit', month:'2-digit', year:'numeric',
                        hour:'2-digit', minute:'2-digit',
                      })}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">{a.duree} min</td>
                    <td className="px-5 py-3.5">
                      {a.type_consultation === 'EN_LIGNE' ? (
                        <div className="flex flex-col gap-2">
                          <span className="badge badge-sky inline-flex items-center gap-1">
                            <Video size={11} />Téléconsultation
                          </span>
                          {a.lien_visio && ['PLANIFIE','CONFIRME','EN_COURS'].includes(a.statut) && (
                            <Link
                              to={`/teleconsultation/${a.id}`}
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold text-white transition-all hover:-translate-y-0.5"
                              style={{ background: 'linear-gradient(180deg,var(--brand-400),var(--brand-600))', boxShadow: '0 4px 12px rgba(42,155,105,0.35)', textDecoration: 'none' }}
                              onClick={e => e.stopPropagation()}
                            >
                              <Video size={11} /> Rejoindre
                            </Link>
                          )}
                          {a.statut === 'TERMINE' && (
                            <span className="text-[10px] text-slate-400 font-semibold">Terminée</span>
                          )}
                        </div>
                      ) : (
                        <span className="badge badge-slate">Cabinet</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      <select
                        value={a.statut}
                        onChange={e => handleStatusChange(a.id, e.target.value)}
                        className={`badge cursor-pointer focus:outline-none ${STATUS_COLORS[a.statut] || 'badge-slate'}`}
                        onClick={e => e.stopPropagation()}
                      >
                        {Object.entries(STATUS_LABELS).map(([v, l]) => (
                          <option key={v} value={v}>{l}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-5 py-3.5">
                      <button
                        onClick={() => setConfirmDelete({ id: a.id, label: new Date(a.date_heure).toLocaleString('fr-FR', { day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' }) })}
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
        {!listLoading && view === 'list' && (
          <Pagination count={count} pageSize={PAGE_SIZE} currentPage={page} onPageChange={setPage} />
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
                  {patients.map(p => <option key={p.id} value={p.id}>{p.nom_complet}</option>)}
                </select>
              </div>
              <div>
                <label className={labelClass}>Médecin</label>
                <select required value={form.medecin} onChange={e => setField('medecin', e.target.value)} className={inputClass}>
                  <option value="">Sélectionner un médecin</option>
                  {doctors.map(d => <option key={d.id} value={d.id}>Dr. {d.last_name} {d.first_name}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={labelClass}>Date et heure</label>
                  <input type="datetime-local" required value={form.date_heure} onChange={e => setField('date_heure', e.target.value)} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Durée (min)</label>
                  <input type="number" min={15} max={120} value={form.duree} onChange={e => setField('duree', e.target.value)} className={inputClass} />
                </div>
              </div>
              <div>
                <label className={labelClass}>Motif de consultation</label>
                <input type="text" required value={form.motif} onChange={e => setField('motif', e.target.value)} placeholder="Ex: Consultation de routine" className={inputClass} />
              </div>

              {/* Type de consultation */}
              <div>
                <label className={labelClass}>Type de consultation</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'PRESENTIEL', label: 'Au cabinet', icon: 'local_hospital' },
                    { value: 'EN_LIGNE',   label: 'Téléconsultation', icon: 'videocam' },
                  ].map(opt => (
                    <label
                      key={opt.value}
                      className={`flex items-center gap-3 rounded-xl border p-3 cursor-pointer transition-colors ${
                        form.type_consultation === opt.value
                          ? 'border-emerald-400 bg-emerald-50'
                          : 'border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      <input
                        type="radio"
                        name="type_consultation"
                        value={opt.value}
                        checked={form.type_consultation === opt.value}
                        onChange={e => setField('type_consultation', e.target.value)}
                        className="w-4 h-4 accent-emerald-500"
                      />
                      <span className="material-symbols-outlined text-[18px] text-slate-500" style={{ fontVariationSettings: "'FILL' 1" }}>{opt.icon}</span>
                      <span className="text-sm font-semibold text-slate-700">{opt.label}</span>
                    </label>
                  ))}
                </div>
                {form.type_consultation === 'EN_LIGNE' && (
                  <p className="mt-1.5 text-[11px] text-sky-600 font-semibold flex items-center gap-1">
                    <span className="material-symbols-outlined text-[13px]">check_circle</span>
                    Un lien Jitsi sera généré automatiquement
                  </p>
                )}
              </div>

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

      {/* ── Confirm delete (corbeille) ── */}
      {confirmDelete && (
        <ConfirmModal
          title="Mettre à la corbeille ?"
          message={`Le rendez-vous du ${confirmDelete.label} sera déplacé dans la corbeille.`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onClose={() => setConfirmDelete(null)}
        />
      )}

      {/* ── Corbeille modal ── */}
      {showTrash && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4" onClick={() => setShowTrash(false)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-rose-50 flex items-center justify-center text-rose-500"><Trash2 size={16} /></div>
                <div>
                  <div className="font-700 text-slate-800 text-sm font-bold">Corbeille — Rendez-vous</div>
                  <div className="text-xs text-slate-400">{trashItems.length} élément{trashItems.length !== 1 ? 's' : ''}</div>
                </div>
              </div>
              <button onClick={() => setShowTrash(false)} className="text-slate-400 hover:text-slate-600 text-xl font-bold">✕</button>
            </div>
            <div className="overflow-y-auto flex-1 px-6 py-4">
              {trashLoading ? (
                <div className="text-center text-slate-400 py-10 text-sm">Chargement…</div>
              ) : trashItems.length === 0 ? (
                <div className="text-center py-14">
                  <div className="text-4xl mb-3">🗑️</div>
                  <div className="text-slate-500 font-semibold">La corbeille est vide</div>
                </div>
              ) : (
                <div className="flex flex-col gap-3">
                  {trashItems.map(a => (
                    <div key={a.id} className="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-200 gap-4">
                      <div className="min-w-0">
                        <div className="font-semibold text-slate-800 text-sm truncate">{a.patient_nom || a.patient_detail?.nom_complet}</div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          {a.date_heure && new Date(a.date_heure).toLocaleString('fr-FR', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })}
                          {a.medecin_nom && ` — ${a.medecin_nom}`}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <button onClick={() => handleRestore(a.id)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-semibold transition-colors">
                          <RotateCcw size={13} /> Restaurer
                        </button>
                        <button onClick={() => handleDeleteForever(a.id)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-600 text-xs font-semibold transition-colors">
                          <Trash2 size={13} /> Supprimer
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
