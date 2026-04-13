import { useEffect, useState, useCallback, useRef } from 'react'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import { SkeletonTable, SkeletonPanel } from '../components/Skeleton'
import ConfirmModal from '../components/ConfirmModal'
import { UserPlus, Search, Eye, Trash2, Phone, Mail, Droplets, ShieldAlert, X } from 'lucide-react'
import useAuthStore from '../store/authStore'

const EMPTY_FORM = {
  first_name: '', last_name: '', date_of_birth: '', gender: 'M',
  national_id: '', phone: '', email: '', address: '',
  blood_group: '', allergies: '', medical_history: '',
}
const BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

function getInitials(p) {
  return `${p?.first_name?.[0] || ''}${p?.last_name?.[0] || ''}`.toUpperCase() || '?'
}

const InputField = ({ label, children }) => (
  <div>
    <label className="label-xs mb-1.5 block">{label}</label>
    {children}
  </div>
)

export default function PatientsPage() {
  const { user } = useAuthStore()
  const isStaff = user?.role !== 'patient'

  const [patients, setPatients]     = useState([])
  const [search, setSearch]         = useState('')
  const [showDrawer, setShowDrawer] = useState(false)
  const [form, setForm]             = useState(EMPTY_FORM)
  const [selected, setSelected]     = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [listLoading, setListLoading]     = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [saving, setSaving]         = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const debounceTimer = useRef(null)

  // ── Fetch helpers ──────────────────────────────────────────────
  const fetchPatients = useCallback(async (query = '') => {
    try {
      const { data } = await api.get(`/api/patients/?search=${encodeURIComponent(query)}`)
      setPatients(data.results || data)
    } catch {
      toast.error('Impossible de charger la liste des patients.')
    }
  }, [])

  useEffect(() => {
    fetchPatients().finally(() => setListLoading(false))
  }, [fetchPatients])

  const fetchDetail = useCallback(async (id) => {
    setSelectedId(id)
    setDetailLoading(true)
    try {
      const { data } = await api.get(`/api/patients/${id}/`)
      setSelected(data)
    } catch {
      toast.error('Impossible de charger la fiche patient.')
    } finally {
      setDetailLoading(false)
    }
  }, [])

  // ── Debounced search ───────────────────────────────────────────
  const handleSearch = (e) => {
    const val = e.target.value
    setSearch(val)
    clearTimeout(debounceTimer.current)
    debounceTimer.current = setTimeout(() => fetchPatients(val), 350)
  }

  // ── Create ─────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/api/patients/', form)
      setShowDrawer(false)
      setForm(EMPTY_FORM)
      await fetchPatients(search)
      toast.success('Patient ajouté avec succès !')
    } catch (err) {
      const detail = err.response?.data
      const msg = typeof detail === 'object'
        ? Object.values(detail).flat()[0]
        : "Erreur lors de la création du patient."
      toast.error(msg)
    } finally {
      setSaving(false)
    }
  }

  // ── Delete ─────────────────────────────────────────────────────
  const handleDelete = async (id) => {
    await api.delete(`/api/patients/${id}/`)
    await fetchPatients(search)
    if (selectedId === id) { setSelected(null); setSelectedId(null) }
    toast.success('Dossier supprimé.')
  }

  const setField = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  return (
    <div className="p-5 md:p-6 space-y-5 min-h-screen">

      {/* ── Page header ── */}
      <section className="surface-panel rounded-3xl px-6 py-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="label-xs text-emerald-700">Dossiers patients</p>
            <h1 className="section-title mt-1.5 text-3xl font-black text-slate-900">Gestion des patients</h1>
            <p className="mt-1.5 text-sm text-slate-500 max-w-lg leading-relaxed">
              Visualisez les dossiers actifs, recherchez en temps réel et ouvrez une fiche sanscutter votre workflow.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <span className="badge badge-emerald">{patients.length} patient{patients.length > 1 ? 's' : ''}</span>
            {isStaff && (
              <button onClick={() => setShowDrawer(true)} className="btn-primary">
                <UserPlus size={16} />
                Nouveau patient
              </button>
            )}
          </div>
        </div>
      </section>

      {/* ── Main grid ── */}
      <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px] items-start">

        {/* Table card */}
        <div className="surface-panel rounded-3xl overflow-hidden">
          {/* Search bar */}
          <div className="px-5 py-4 border-b border-slate-100">
            <div className="relative">
              <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Rechercher par nom ou CIN…"
                value={search}
                onChange={handleSearch}
                className="w-full rounded-2xl border border-slate-200 bg-white py-2.5 pl-11 pr-4 text-sm focus:border-emerald-400 focus:outline-none focus:ring-3 focus:ring-emerald-100 transition-all"
              />
            </div>
          </div>

          {/* Table */}
          {listLoading ? (
            <SkeletonTable rows={6} cols={5} />
          ) : (
            <div className="overflow-x-auto soft-scrollbar">
              <table className="w-full min-w-[560px] text-left">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-100">
                    {['Patient', 'Date de naissance', 'CIN', 'Téléphone', 'Groupe', ''].map(h => (
                      <th key={h} className="px-5 py-3.5 label-xs">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {patients.map(p => (
                    <tr
                      key={p.id}
                      onClick={() => fetchDetail(p.id)}
                      className={`table-row-hover ${selectedId === p.id ? 'table-row-active' : ''}`}
                    >
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-2xl bg-emerald-100 flex items-center justify-center text-sm font-bold text-emerald-700 shrink-0">
                            {p.full_name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || '?'}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-slate-900">{p.full_name}</p>
                            <p className="text-xs text-slate-400">{p.age ? `${p.age} ans` : '—'}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-sm text-slate-600">{p.date_of_birth || '—'}</td>
                      <td className="px-5 py-3.5 text-sm text-slate-600">{p.national_id || '—'}</td>
                      <td className="px-5 py-3.5 text-sm text-slate-600">{p.phone || '—'}</td>
                      <td className="px-5 py-3.5">
                        {p.blood_group
                          ? <span className="badge badge-rose">{p.blood_group}</span>
                          : <span className="text-slate-300 text-sm">—</span>}
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-1.5" onClick={e => e.stopPropagation()}>
                          <button
                            onClick={() => fetchDetail(p.id)}
                            className="w-8 h-8 rounded-xl bg-slate-100 hover:bg-emerald-100 hover:text-emerald-700 text-slate-500 flex items-center justify-center transition-colors"
                            title="Voir la fiche"
                          >
                            <Eye size={15} />
                          </button>
                          {isStaff && (
                            <button
                              onClick={() => setConfirmDelete({ id: p.id, name: p.full_name })}
                              className="w-8 h-8 rounded-xl bg-slate-100 hover:bg-rose-100 hover:text-rose-700 text-slate-500 flex items-center justify-center transition-colors"
                              title="Supprimer"
                            >
                              <Trash2 size={15} />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                  {patients.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-16 text-center">
                        <div className="flex flex-col items-center gap-3 text-slate-400">
                          <Search size={32} className="opacity-30" />
                          <p className="text-sm font-medium">Aucun patient trouvé</p>
                          {search && <p className="text-xs">Essayez un autre terme de recherche</p>}
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Detail panel */}
        <aside
          className="surface-panel rounded-3xl overflow-y-auto soft-scrollbar sticky top-6"
          style={{ maxHeight: 'calc(100vh - 112px)' }}
        >
          {detailLoading ? (
            <SkeletonPanel />
          ) : selected ? (
            <div className="p-5 space-y-5">
              {/* Patient header */}
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 rounded-[1.4rem] bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-xl font-black text-white shrink-0">
                  {getInitials(selected)}
                </div>
                <div>
                  <p className="label-xs text-slate-400">Fiche patient</p>
                  <h2 className="section-title mt-1 text-xl font-black text-slate-900">
                    {selected.first_name} {selected.last_name}
                  </h2>
                  <p className="text-sm text-slate-500 mt-0.5">
                    {selected.gender === 'M' ? 'Masculin' : 'Féminin'}
                    {selected.age ? ` · ${selected.age} ans` : ''}
                  </p>
                </div>
              </div>

              {/* IDs */}
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-2xl bg-slate-50 p-3.5">
                  <p className="label-xs mb-1.5">CIN</p>
                  <p className="text-sm font-semibold text-slate-900">{selected.national_id || '—'}</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-3.5">
                  <p className="label-xs mb-1.5">Naissance</p>
                  <p className="text-sm font-semibold text-slate-900">{selected.date_of_birth || '—'}</p>
                </div>
              </div>

              {/* Contact */}
              <div className="space-y-2">
                {[
                  { icon: Phone, val: selected.phone, fallback: 'Téléphone non renseigné', cls: 'text-emerald-600' },
                  { icon: Mail,  val: selected.email, fallback: 'Email non renseigné',    cls: 'text-indigo-500' },
                  { icon: Droplets, val: selected.blood_group, fallback: 'Groupe sanguin non renseigné', cls: 'text-rose-500' },
                ].map((item) => {
                  const { icon: ContactIcon, val, fallback, cls } = item
                  return (
                    <div key={fallback} className="flex items-center gap-3 rounded-xl bg-slate-50 px-4 py-2.5 text-sm text-slate-700">
                      <ContactIcon size={15} className={`shrink-0 ${cls}`} />
                      <span className={val ? '' : 'text-slate-400 text-xs'}>{val || fallback}</span>
                    </div>
                  )
                })}
              </div>

              {/* Clinical info */}
              <div className="rounded-2xl bg-gradient-to-br from-amber-50 to-rose-50 border border-amber-100 p-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-slate-800 mb-4">
                  <ShieldAlert size={16} className="text-amber-600" />
                  Informations cliniques
                </div>
                {[
                  { label: 'Allergies', val: selected.allergies, empty: 'Aucune allergie renseignée.' },
                  { label: 'Antécédents médicaux', val: selected.medical_history, empty: 'Aucun antécédent saisi.' },
                  { label: 'Adresse', val: selected.address, empty: 'Adresse non renseignée.' },
                ].map(({ label, val, empty }) => (
                  <div key={label} className="mb-3 last:mb-0">
                    <p className="label-xs mb-1">{label}</p>
                    <p className="text-sm text-slate-700 leading-6">{val || <span className="text-slate-400">{empty}</span>}</p>
                  </div>
                ))}
              </div>

              {/* Delete */}
              {isStaff && (
                <button
                  onClick={() => setConfirmDelete({ id: selected.id, name: `${selected.first_name} ${selected.last_name}` })}
                  className="flex w-full items-center justify-center gap-2 rounded-2xl bg-rose-50 px-4 py-2.5 text-sm font-semibold text-rose-700 hover:bg-rose-100 transition-colors"
                >
                  <Trash2 size={15} /> Supprimer le dossier
                </button>
              )}
            </div>
          ) : (
            <div className="p-5 flex h-full min-h-[360px] flex-col items-center justify-center text-center rounded-[1.6rem] border-2 border-dashed border-slate-100">
              <div className="w-14 h-14 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-500 mb-4">
                <Eye size={24} />
              </div>
              <h3 className="section-title text-lg font-black text-slate-900">Sélectionner un dossier</h3>
              <p className="mt-2 text-sm text-slate-400 max-w-[220px] leading-6">
                Cliquez sur une ligne pour afficher les informations du patient.
              </p>
            </div>
          )}
        </aside>
      </section>

      {/* ── Side drawer: New patient ── */}
      {showDrawer && (
        <>
          <div className="side-drawer-overlay" onClick={() => setShowDrawer(false)} />
          <div className="side-drawer soft-scrollbar">
            {/* Drawer header */}
            <div className="sticky top-0 bg-white z-10 px-6 py-5 border-b border-slate-100 flex items-center justify-between">
              <div>
                <p className="label-xs text-emerald-700">Nouveau dossier</p>
                <h2 className="section-title mt-1 text-xl font-black text-slate-900">Ajouter un patient</h2>
              </div>
              <button
                onClick={() => setShowDrawer(false)}
                className="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <InputField label="Prénom *">
                  <input type="text" required value={form.first_name} onChange={e => setField('first_name', e.target.value)} className="input-base" />
                </InputField>
                <InputField label="Nom *">
                  <input type="text" required value={form.last_name} onChange={e => setField('last_name', e.target.value)} className="input-base" />
                </InputField>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <InputField label="Date de naissance *">
                  <input type="date" required value={form.date_of_birth} onChange={e => setField('date_of_birth', e.target.value)} className="input-base" />
                </InputField>
                <InputField label="Genre">
                  <select value={form.gender} onChange={e => setField('gender', e.target.value)} className="input-base">
                    <option value="M">Masculin</option>
                    <option value="F">Féminin</option>
                  </select>
                </InputField>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <InputField label="CIN *">
                  <input type="text" required value={form.national_id} onChange={e => setField('national_id', e.target.value)} className="input-base" />
                </InputField>
                <InputField label="Groupe sanguin">
                  <select value={form.blood_group} onChange={e => setField('blood_group', e.target.value)} className="input-base">
                    <option value="">Non renseigné</option>
                    {BLOOD_TYPES.map(b => <option key={b} value={b}>{b}</option>)}
                  </select>
                </InputField>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <InputField label="Téléphone">
                  <input type="tel" value={form.phone} onChange={e => setField('phone', e.target.value)} className="input-base" />
                </InputField>
                <InputField label="Email">
                  <input type="email" value={form.email} onChange={e => setField('email', e.target.value)} className="input-base" />
                </InputField>
              </div>

              <InputField label="Adresse">
                <input type="text" value={form.address} onChange={e => setField('address', e.target.value)} className="input-base" />
              </InputField>

              <InputField label="Allergies">
                <textarea rows={2} value={form.allergies} onChange={e => setField('allergies', e.target.value)} className="input-base resize-none" />
              </InputField>

              <InputField label="Antécédents médicaux">
                <textarea rows={2} value={form.medical_history} onChange={e => setField('medical_history', e.target.value)} className="input-base resize-none" />
              </InputField>

              {/* Actions */}
              <div className="pt-2 flex gap-3">
                <button type="button" onClick={() => setShowDrawer(false)} className="btn-ghost flex-1">
                  Annuler
                </button>
                <button type="submit" disabled={saving} className="btn-primary flex-1 justify-center">
                  {saving ? 'Enregistrement…' : 'Enregistrer'}
                </button>
              </div>
            </form>
          </div>
        </>
      )}

      {/* ── Confirm delete modal ── */}
      {confirmDelete && (
        <ConfirmModal
          title="Supprimer le dossier ?"
          message={`Le dossier de ${confirmDelete.name} sera définitivement supprimé. Cette action est irréversible.`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onClose={() => setConfirmDelete(null)}
          variant="danger"
        />
      )}
    </div>
  )
}
