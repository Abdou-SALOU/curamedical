import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import { SkeletonTable, SkeletonPanel } from '../components/Skeleton'
import ConfirmModal from '../components/ConfirmModal'
import Pagination from '../components/Pagination'
import { UserPlus, Search, Eye, Trash2, Phone, Mail, Droplets, ShieldAlert, X, Clock, Check, UserCheck } from 'lucide-react'
import useAuthStore from '../store/authStore'

const PAGE_SIZE = 10

const EMPTY_FORM = {
  prenom: '', nom: '', date_naissance: '', sexe: 'M',
  cin: '', telephone: '', email: '', adresse: '',
  groupe_sanguin: '', allergies: '', antecedents_medicaux: '',
}
const BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

function getInitials(p) {
  return `${p?.prenom?.[0] || ''}${p?.nom?.[0] || ''}`.toUpperCase() || '?'
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
  const [count, setCount]           = useState(0)
  const [page, setPage]             = useState(1)
  const [search, setSearch]         = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)
  const [showDrawer, setShowDrawer] = useState(false)
  const [form, setForm]             = useState(EMPTY_FORM)
  const [selected, setSelected]     = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [listLoading, setListLoading]     = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [saving, setSaving]         = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(null)

  // ── Demandes d'inscription en attente de validation ────────────
  const [tab, setTab]               = useState('actifs') // 'actifs' | 'attente'
  const [pending, setPending]       = useState([])
  const [pendingLoading, setPendingLoading] = useState(false)
  const [actionId, setActionId]     = useState(null)
  const [confirmRefuse, setConfirmRefuse] = useState(null)

  // ── Recherche avec debounce ────────────────────────────────────
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 350)
    return () => clearTimeout(timer)
  }, [search])

  // ── Chargement paginé côté serveur ─────────────────────────────
  useEffect(() => {
    let ignore = false
    const charger = async () => {
      try {
        const { data } = await api.get(
          `/api/patients/?page_size=${PAGE_SIZE}&page=${page}&search=${encodeURIComponent(debouncedSearch)}`
        )
        if (ignore) return
        const results = data.results || data
        // Page devenue vide (ex: dernier élément supprimé) → reculer d'une page
        if (results.length === 0 && page > 1) {
          setPage(p => Math.max(1, p - 1))
          return
        }
        setPatients(results)
        setCount(data.count ?? results.length)
      } catch {
        if (!ignore) toast.error('Impossible de charger la liste des patients.')
      } finally {
        if (!ignore) setListLoading(false)
      }
    }
    charger()
    return () => { ignore = true }
  }, [page, debouncedSearch, refreshKey])

  const refresh = () => setRefreshKey(k => k + 1)

  // ── Chargement des demandes en attente (badge + onglet) ────────
  useEffect(() => {
    if (!isStaff) return
    let ignore = false
    const charger = async () => {
      setPendingLoading(true)
      try {
        const { data } = await api.get('/api/patients/en-attente/')
        if (!ignore) setPending(data.results || data)
      } catch {
        if (!ignore) toast.error('Impossible de charger les demandes en attente.')
      } finally {
        if (!ignore) setPendingLoading(false)
      }
    }
    charger()
    return () => { ignore = true }
  }, [isStaff, refreshKey])

  // ── Valider / Refuser une inscription ──────────────────────────
  const handleValider = async (id) => {
    setActionId(id)
    try {
      await api.post(`/api/patients/${id}/valider/`)
      toast.success('Inscription validée. Le patient peut maintenant prendre rendez-vous.')
      refresh()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Impossible de valider cette inscription.')
    } finally {
      setActionId(null)
    }
  }

  const handleRefuser = async (id) => {
    setActionId(id)
    try {
      await api.post(`/api/patients/${id}/refuser/`)
      toast.success('Inscription refusée.')
      refresh()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Impossible de refuser cette inscription.')
    } finally {
      setActionId(null)
    }
  }

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

  // ── Search ─────────────────────────────────────────────────────
  const handleSearch = (e) => {
    setSearch(e.target.value)
    setPage(1)
  }

  // ── Create ─────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/api/patients/', form)
      setShowDrawer(false)
      setForm(EMPTY_FORM)
      refresh()
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

  // ── Archive ────────────────────────────────────────────────────
  const handleArchive = async (id) => {
    try {
      await api.patch(`/api/patients/${id}/archiver/`)
      refresh()
      if (selectedId === id) { setSelected(null); setSelectedId(null) }
      toast.success('Patient archivé.')
    } catch {
      toast.error("Impossible d'archiver ce patient.")
    }
  }

  // ── Delete ─────────────────────────────────────────────────────
  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/patients/${id}/`)
      refresh()
      if (selectedId === id) { setSelected(null); setSelectedId(null) }
      toast.success('Dossier supprimé.')
    } catch {
      toast.error('Impossible de supprimer ce dossier.')
    }
  }

  const setField = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  return (
    <div className="cm-page">

      {/* ── Page header ── */}
      <div className="cm-page-head">
        <div>
          <div className="cm-eyebrow">Dossiers patients</div>
          <div className="cm-title">Gestion des patients</div>
          <div className="cm-sub">{count} patient{count > 1 ? 's' : ''} enregistré{count > 1 ? 's' : ''}</div>
        </div>
        <div className="cm-row" style={{ gap: 12 }}>
          {isStaff && (
            <>
              <Link to="/patients/trash" className="cm-btn cm-btn-ghost" style={{ textDecoration: 'none' }} title="Patients archivés">
                <Trash2 size={15} /> Corbeille
              </Link>
              <button onClick={() => setShowDrawer(true)} className="cm-btn cm-btn-brand">
                <UserPlus size={16} />
                Nouveau patient
              </button>
            </>
          )}
        </div>
      </div>

      {/* ── Onglets (staff) ── */}
      {isStaff && (
        <div className="flex rounded-xl bg-slate-100 p-1 gap-1 mb-4 w-fit">
          {[['actifs', 'Patients'], ['attente', 'Demandes en attente']].map(([v, label]) => (
            <button
              key={v}
              onClick={() => setTab(v)}
              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                tab === v ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              {v === 'attente' && <Clock size={13} />}
              {label}
              {v === 'attente' && pending.length > 0 && (
                <span className="ml-1 inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full bg-amber-500 text-white text-[10px] font-bold">
                  {pending.length}
                </span>
              )}
            </button>
          ))}
        </div>
      )}

      {/* ── Onglet : Demandes en attente ── */}
      {isStaff && tab === 'attente' && (
        <div className="cm-card" style={{ padding: 0, overflow: 'hidden' }}>
          {pendingLoading ? (
            <SkeletonTable rows={4} cols={4} />
          ) : pending.length === 0 ? (
            <div className="py-16 text-center">
              <div className="flex flex-col items-center gap-3 text-slate-400">
                <UserCheck size={32} className="opacity-30" />
                <p className="text-sm font-medium">Aucune demande en attente</p>
                <p className="text-xs">Les inscriptions depuis le portail patient apparaîtront ici.</p>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto soft-scrollbar">
              <table className="w-full min-w-[640px] text-left">
                <thead>
                  <tr className="bg-amber-50 border-b border-amber-100">
                    {['Patient', 'Inscrit le', 'Contact', 'CIN', 'Action'].map(h => (
                      <th key={h} className="px-5 py-3.5 label-xs">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {pending.map(p => (
                    <tr key={p.id} className="table-row-hover">
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-2xl bg-amber-100 flex items-center justify-center text-sm font-bold text-amber-700 shrink-0">
                            {getInitials(p)}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-slate-900">{p.prenom} {p.nom}</p>
                            <p className="text-xs text-slate-400">{p.age ? `${p.age} ans` : '—'} · {p.sexe === 'M' ? 'Masculin' : 'Féminin'}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-sm text-slate-600">
                        {p.cree_le ? new Date(p.cree_le).toLocaleDateString('fr-FR') : '—'}
                      </td>
                      <td className="px-5 py-3.5 text-sm text-slate-600">
                        <div className="flex flex-col">
                          <span>{p.telephone || '—'}</span>
                          <span className="text-xs text-slate-400">{p.email || '—'}</span>
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-sm text-slate-600">{p.cin || '—'}</td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleValider(p.id)}
                            disabled={actionId === p.id}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-semibold transition-colors disabled:opacity-50"
                          >
                            <Check size={13} /> Valider
                          </button>
                          <button
                            onClick={() => setConfirmRefuse({ id: p.id, name: `${p.prenom} ${p.nom}` })}
                            disabled={actionId === p.id}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-600 text-xs font-semibold transition-colors disabled:opacity-50"
                          >
                            <X size={13} /> Refuser
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Main grid ── */}
      {(!isStaff || tab === 'actifs') && (
      <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px] items-start">

        {/* Table card */}
        <div className="cm-card" style={{ padding: 0, overflow: 'hidden' }}>
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
                            {p.nom_complet?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || '?'}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-slate-900">{p.nom_complet}</p>
                            <p className="text-xs text-slate-400">{p.age ? `${p.age} ans` : '—'}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-sm text-slate-600">{p.date_naissance || '—'}</td>
                      <td className="px-5 py-3.5 text-sm text-slate-600">{p.cin || '—'}</td>
                      <td className="px-5 py-3.5 text-sm text-slate-600">{p.telephone || '—'}</td>
                      <td className="px-5 py-3.5">
                        {p.groupe_sanguin
                          ? <span className="badge badge-rose">{p.groupe_sanguin}</span>
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
                              onClick={() => setConfirmDelete({ id: p.id, name: p.nom_complet })}
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
          {!listLoading && (
            <Pagination count={count} pageSize={PAGE_SIZE} currentPage={page} onPageChange={setPage} />
          )}
        </div>

        {/* Detail panel */}
        <aside
          className="cm-card soft-scrollbar sticky top-6"
          style={{ maxHeight: 'calc(100vh - 112px)', overflow: 'hidden', overflowY: 'auto' }}
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
                    {selected.prenom} {selected.nom}
                  </h2>
                  <p className="text-sm text-slate-500 mt-0.5">
                    {selected.sexe === 'M' ? 'Masculin' : 'Féminin'}
                    {selected.age ? ` · ${selected.age} ans` : ''}
                  </p>
                </div>
              </div>

              {/* IDs */}
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-2xl bg-slate-50 p-3.5">
                  <p className="label-xs mb-1.5">CIN</p>
                  <p className="text-sm font-semibold text-slate-900">{selected.cin || '—'}</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-3.5">
                  <p className="label-xs mb-1.5">Naissance</p>
                  <p className="text-sm font-semibold text-slate-900">{selected.date_naissance || '—'}</p>
                </div>
              </div>

              {/* Contact */}
              <div className="space-y-2">
                {[
                  { icon: Phone, val: selected.telephone, fallback: 'Téléphone non renseigné', cls: 'text-emerald-600' },
                  { icon: Mail,  val: selected.email, fallback: 'Email non renseigné',    cls: 'text-indigo-500' },
                  { icon: Droplets, val: selected.groupe_sanguin, fallback: 'Groupe sanguin non renseigné', cls: 'text-rose-500' },
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
                  { label: 'Antécédents médicaux', val: selected.antecedents_medicaux, empty: 'Aucun antécédent saisi.' },
                  { label: 'Adresse', val: selected.adresse, empty: 'Adresse non renseignée.' },
                ].map(({ label, val, empty }) => (
                  <div key={label} className="mb-3 last:mb-0">
                    <p className="label-xs mb-1">{label}</p>
                    <p className="text-sm text-slate-700 leading-6">{val || <span className="text-slate-400">{empty}</span>}</p>
                  </div>
                ))}
              </div>

              {/* Delete */}
              {isStaff && (
                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => handleArchive(selected.id)}
                    className="flex w-full items-center justify-center gap-2 rounded-2xl bg-amber-50 px-4 py-2.5 text-sm font-semibold text-amber-700 hover:bg-amber-100 transition-colors"
                  >
                    <span className="material-symbols-outlined text-[16px]">archive</span>
                    Archiver le dossier
                  </button>
                  <button
                    onClick={() => setConfirmDelete({ id: selected.id, name: `${selected.prenom} ${selected.nom}` })}
                    className="flex w-full items-center justify-center gap-2 rounded-2xl bg-rose-50 px-4 py-2.5 text-sm font-semibold text-rose-700 hover:bg-rose-100 transition-colors"
                  >
                    <Trash2 size={15} /> Supprimer définitivement
                  </button>
                </div>
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
      )}

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
                  <input type="text" required value={form.prenom} onChange={e => setField('prenom', e.target.value)} className="input-base" />
                </InputField>
                <InputField label="Nom *">
                  <input type="text" required value={form.nom} onChange={e => setField('nom', e.target.value)} className="input-base" />
                </InputField>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <InputField label="Date de naissance *">
                  <input type="date" required value={form.date_naissance} onChange={e => setField('date_naissance', e.target.value)} className="input-base" />
                </InputField>
                <InputField label="Genre">
                  <select value={form.sexe} onChange={e => setField('sexe', e.target.value)} className="input-base">
                    <option value="M">Masculin</option>
                    <option value="F">Féminin</option>
                  </select>
                </InputField>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <InputField label="CIN *">
                  <input type="text" required value={form.cin} onChange={e => setField('cin', e.target.value)} className="input-base" />
                </InputField>
                <InputField label="Groupe sanguin">
                  <select value={form.groupe_sanguin} onChange={e => setField('groupe_sanguin', e.target.value)} className="input-base">
                    <option value="">Non renseigné</option>
                    {BLOOD_TYPES.map(b => <option key={b} value={b}>{b}</option>)}
                  </select>
                </InputField>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <InputField label="Téléphone">
                  <input type="tel" value={form.telephone} onChange={e => setField('telephone', e.target.value)} className="input-base" />
                </InputField>
                <InputField label="Email">
                  <input type="email" value={form.email} onChange={e => setField('email', e.target.value)} className="input-base" />
                </InputField>
              </div>

              <InputField label="Adresse">
                <input type="text" value={form.adresse} onChange={e => setField('adresse', e.target.value)} className="input-base" />
              </InputField>

              <InputField label="Allergies">
                <textarea rows={2} value={form.allergies} onChange={e => setField('allergies', e.target.value)} className="input-base resize-none" />
              </InputField>

              <InputField label="Antécédents médicaux">
                <textarea rows={2} value={form.antecedents_medicaux} onChange={e => setField('antecedents_medicaux', e.target.value)} className="input-base resize-none" />
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

      {/* ── Confirm refuse inscription ── */}
      {confirmRefuse && (
        <ConfirmModal
          title="Refuser cette inscription ?"
          message={`La demande d'inscription de ${confirmRefuse.name} sera refusée et archivée. Le patient ne pourra pas prendre de rendez-vous.`}
          onConfirm={() => { handleRefuser(confirmRefuse.id); setConfirmRefuse(null) }}
          onClose={() => setConfirmRefuse(null)}
          variant="danger"
        />
      )}
    </div>
  )
}
