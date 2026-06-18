import { useEffect, useState, useCallback } from 'react'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import { SkeletonTable } from '../components/Skeleton'
import ConfirmModal from '../components/ConfirmModal'
import Pagination from '../components/Pagination'
import { FileText, Plus, Download, Trash2, Pill, X, Eye, RotateCcw } from 'lucide-react'

const PAGE_SIZE = 10

const EMPTY_ITEM = { medicament: '', dosage: '', frequence: '', duree: '', instructions: '' }
const EMPTY_FORM = { consultation: '', notes_generales: '', lignes: [{ ...EMPTY_ITEM }] }

const inputClass = "input-base"
const labelClass = "label-xs mb-1.5 block"

/* ── Live prescription preview ──────────────────────────────── */
function PrescriptionPreview({ form, consultations }) {
  const consult = consultations.find(c => String(c.id) === String(form.consultation))
  const items = form.lignes.filter(i => i.medicament.trim())

  return (
    <div className="rounded-2xl border-2 border-dashed border-slate-200 bg-white p-5 text-sm h-full min-h-[200px]">
      {/* Header mock */}
      <div className="flex items-start justify-between mb-5 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-5 h-5 rounded-md bg-emerald-500 flex items-center justify-center">
              <span className="text-white text-[9px] font-black">C</span>
            </div>
            <p className="font-black text-slate-900 text-base" style={{ fontFamily: 'Manrope' }}>CuraMedical</p>
          </div>
          <p className="text-xs text-slate-400">Ordonnance médicale</p>
        </div>
        <p className="text-xs text-slate-400">{new Date().toLocaleDateString('fr-FR')}</p>
      </div>

      {/* Patient / Diagnosis */}
      {consult ? (
        <div className="mb-4">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Patient</p>
          <p className="font-semibold text-slate-800">{consult.patient_nom || '—'}</p>
          <p className="text-xs text-slate-400 mt-0.5">Diagnostic : {consult.diagnostic || '—'}</p>
        </div>
      ) : (
        <div className="mb-4 p-3 rounded-xl bg-slate-50 text-xs text-slate-400 text-center">
          Sélectionnez une consultation pour afficher l'aperçu
        </div>
      )}

      {/* Medications */}
      {items.length > 0 ? (
        <div className="space-y-2">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Médicaments prescrits</p>
          {items.map((item, i) => (
            <div key={i} className="flex items-start gap-2 p-2.5 rounded-xl bg-emerald-50 border border-emerald-100">
              <Pill size={12} className="text-emerald-600 mt-0.5 shrink-0" />
              <div className="text-xs">
                <p className="font-bold text-slate-900">{item.medicament} {item.dosage && `· ${item.dosage}`}</p>
                {item.frequence && <p className="text-slate-500">{item.frequence}{item.duree && ` — ${item.duree}`}</p>}
                {item.instructions && <p className="text-slate-400 italic">{item.instructions}</p>}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-3 rounded-xl bg-slate-50 text-xs text-slate-400 text-center">
          Les médicaments apparaîtront ici
        </div>
      )}

      {form.notes_generales && (
        <div className="mt-3 p-2.5 rounded-xl bg-amber-50 border border-amber-100 text-xs text-amber-800">
          <span className="font-semibold">Instructions : </span>{form.notes_generales}
        </div>
      )}

      <div className="mt-5 pt-4 border-t border-slate-100 flex justify-end">
        <div className="text-right">
          <div className="w-24 h-px bg-slate-300 mb-1 ml-auto" />
          <p className="text-[10px] text-slate-400">Signature du médecin</p>
        </div>
      </div>
    </div>
  )
}

export default function PrescriptionsPage() {
  const [prescriptions, setPrescriptions] = useState([])
  const [count, setCount] = useState(0)
  const [page, setPage] = useState(1)
  const [consultations, setConsultations] = useState([])
  const [showForm, setShowForm]     = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [form, setForm]             = useState(EMPTY_FORM)
  const [listLoading, setListLoading] = useState(true)
  const [saving, setSaving]         = useState(false)
  const [downloading, setDownloading] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [showTrash, setShowTrash]         = useState(false)
  const [trashItems, setTrashItems]       = useState([])
  const [trashLoading, setTrashLoading]   = useState(false)

  const fetchTrash = async () => {
    setTrashLoading(true)
    try {
      const { data } = await api.get('/api/prescriptions/corbeille/')
      setTrashItems(data.results || data)
    } catch { toast.error('Impossible de charger la corbeille.') }
    finally { setTrashLoading(false) }
  }

  const handleRestore = async (id) => {
    try {
      await api.post(`/api/prescriptions/${id}/restaurer/`)
      setTrashItems(prev => prev.filter(p => p.id !== id))
      await fetchAll()
      toast.success('Ordonnance restaurée.')
    } catch { toast.error('Impossible de restaurer l\'ordonnance.') }
  }

  const handleDeleteForever = async (id) => {
    try {
      await api.delete(`/api/prescriptions/${id}/supprimer-definitif/`)
      setTrashItems(prev => prev.filter(p => p.id !== id))
      toast.success('Supprimée définitivement.')
    } catch { toast.error('Impossible de supprimer définitivement.') }
  }

  const fetchAll = useCallback(async () => {
    const [prescs, consults] = await Promise.allSettled([
      api.get(`/api/prescriptions/?page_size=${PAGE_SIZE}&page=${page}`),
      api.get('/api/consultations/?page_size=500'),
    ])
    if (prescs.status === 'fulfilled') {
      const results = prescs.value.data.results || prescs.value.data
      setPrescriptions(results)
      setCount(prescs.value.data.count ?? results.length)
    } else {
      toast.error('Impossible de charger les ordonnances.')
    }
    if (consults.status === 'fulfilled') setConsultations(consults.value.data.results || consults.value.data)
  }, [page])

  useEffect(() => { fetchAll().finally(() => setListLoading(false)) }, [fetchAll])

  const handleItemChange = (index, field, value) => {
    setForm(prev => {
      const lignes = [...prev.lignes]
      lignes[index] = { ...lignes[index], [field]: value }
      return { ...prev, lignes }
    })
  }
  const addItem = () => setForm(prev => ({ ...prev, lignes: [...prev.lignes, { ...EMPTY_ITEM }] }))
  const removeItem = (i) => setForm(prev => ({ ...prev, lignes: prev.lignes.filter((_, idx) => idx !== i) }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/api/prescriptions/', form)
      setShowForm(false)
      setForm(EMPTY_FORM)
      await fetchAll()
      toast.success("Ordonnance créée avec succès !")
    } catch (err) {
      const data = err.response?.data
      let msg = "Erreur lors de la création de l'ordonnance."
      if (typeof data === 'string') msg = data
      else if (data?.detail) msg = data.detail
      else if (data?.non_field_errors) msg = data.non_field_errors[0]
      else if (typeof data === 'object') {
        const first = Object.entries(data)[0]
        if (first) msg = `${first[0]} : ${Array.isArray(first[1]) ? first[1][0] : first[1]}`
      }
      toast.error(msg)
    } finally {
      setSaving(false)
    }
  }

  const handleDownload = async (id) => {
    setDownloading(id)
    try {
      const response = await api.get(`/api/prescriptions/${id}/ordonnance-pdf/`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `ordonnance_${id}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      toast.success('PDF téléchargé !')
    } catch {
      toast.error('Erreur lors du téléchargement du PDF.')
    } finally {
      setDownloading(null)
    }
  }

  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/prescriptions/${id}/`)
      await fetchAll()
      toast.success('Déplacée dans la corbeille.')
    } catch {
      toast.error('Impossible de supprimer cette ordonnance.')
    }
  }

  const setField = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  return (
    <div className="cm-page">

      {/* Header */}
      <div className="cm-page-head">
        <div>
          <div className="cm-eyebrow">Documents médicaux</div>
          <div className="cm-title">Ordonnances</div>
          <div className="cm-sub">{count} ordonnance{count > 1 ? 's' : ''} émise{count > 1 ? 's' : ''}</div>
        </div>
        <button onClick={() => { setShowTrash(true); fetchTrash() }} className="cm-btn cm-btn-ghost" title="Corbeille">
          <Trash2 size={15} /> Corbeille
        </button>
        <button onClick={() => setShowForm(true)} className="cm-btn cm-btn-brand">
          <Plus size={16} />
          Nouvelle ordonnance
        </button>
      </div>

      {/* Table */}
      <div className="cm-card" style={{ padding: 0, overflow: 'hidden' }}>
        {listLoading ? (
          <SkeletonTable rows={5} cols={4} />
        ) : (
          <div className="overflow-x-auto soft-scrollbar">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  {['Patient', 'Médecin', 'Médicaments', 'Date', ''].map(h => (
                    <th key={h} className="px-5 py-3.5 label-xs">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {prescriptions.map(p => (
                  <tr key={p.id} className="table-row-hover">
                    <td className="px-5 py-3.5">
                      <p className="text-sm font-semibold text-slate-900">{p.patient_nom || '—'}</p>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">{p.medecin_nom || '—'}</td>
                    <td className="px-5 py-3.5">
                      <div className="flex flex-wrap gap-1">
                        {(p.lignes || []).slice(0, 3).map((item, i) => (
                          <span key={i} className="badge badge-emerald">{item.medicament}</span>
                        ))}
                        {(p.lignes || []).length > 3 && (
                          <span className="badge badge-slate">+{p.lignes.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">
                      {new Date(p.cree_le).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => handleDownload(p.id)}
                          disabled={downloading === p.id}
                          className="flex items-center gap-1.5 badge badge-indigo hover:bg-indigo-200 transition-colors cursor-pointer disabled:opacity-50"
                        >
                          {downloading === p.id
                            ? <span className="w-3 h-3 border-2 border-indigo-400/30 border-t-indigo-600 rounded-full animate-spin" />
                            : <Download size={11} />}
                          PDF
                        </button>
                        <button
                          onClick={() => setConfirmDelete({ id: p.id, name: p.patient_nom })}
                          className="w-7 h-7 rounded-lg hover:bg-rose-100 hover:text-rose-600 text-slate-400 flex items-center justify-center transition-colors"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {prescriptions.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-16 text-center">
                      <div className="flex flex-col items-center gap-3 text-slate-400">
                        <FileText size={32} className="opacity-30" />
                        <p className="text-sm font-medium">Aucune ordonnance enregistrée</p>
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

      {/* ── Create form modal ── */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-start justify-center p-4 bg-slate-950/40 backdrop-blur-sm overflow-y-auto">
          <div
            className="surface-panel-strong w-full max-w-4xl rounded-3xl overflow-hidden my-6 flex flex-col"
            style={{ animation: 'confirmIn 0.3s cubic-bezier(0.16,1,0.3,1) both', maxHeight: 'calc(100vh - 48px)' }}
          >
            {/* Modal header */}
            <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between shrink-0">
              <div>
                <p className="label-xs text-emerald-700">Documents médicaux</p>
                <h2 className="section-title text-xl font-black text-slate-900 mt-1">Nouvelle ordonnance</h2>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setShowPreview(p => !p)}
                  className="flex items-center gap-1.5 rounded-xl bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-200 transition-colors xl:hidden"
                >
                  <Eye size={13} />{showPreview ? 'Masquer' : 'Aperçu'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500 transition-colors"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <div className="grid xl:grid-cols-[1fr_340px] divide-x divide-slate-100 flex-1 overflow-hidden min-h-0">
              {/* Form */}
              <form id="prescription-form" onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto soft-scrollbar">
                {/* Consultation picker */}
                <div>
                  <label className={labelClass}>Consultation associée *</label>
                  <select
                    required
                    value={form.consultation}
                    onChange={e => setField('consultation', e.target.value)}
                    className={inputClass}
                  >
                    <option value="">Sélectionner une consultation</option>
                    {consultations.map(c => (
                      <option key={c.id} value={c.id}>
                        {c.patient_nom} — {c.diagnostic || 'Sans diagnostic'} ({new Date(c.date_consultation).toLocaleDateString('fr-FR')})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Medications */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className={labelClass}>Médicaments prescrits</span>
                    <button
                      type="button"
                      onClick={addItem}
                      className="flex items-center gap-1 text-emerald-600 hover:text-emerald-700 text-xs font-semibold transition-colors"
                    >
                      <Plus size={13} />Ajouter
                    </button>
                  </div>
                  <div className="space-y-3">
                    {form.lignes.map((item, i) => (
                      <div key={i} className="rounded-2xl bg-slate-50 border border-slate-100 p-4">
                        <div className="flex justify-between items-center mb-3">
                          <div className="flex items-center gap-2">
                            <Pill size={14} className="text-emerald-600" />
                            <span className="text-sm font-semibold text-slate-700">Médicament {i + 1}</span>
                          </div>
                          {form.lignes.length > 1 && (
                            <button
                              type="button"
                              onClick={() => removeItem(i)}
                              className="w-6 h-6 rounded-full bg-slate-200 hover:bg-rose-200 hover:text-rose-600 text-slate-500 flex items-center justify-center text-sm transition-colors"
                            >
                              <X size={12} />
                            </button>
                          )}
                        </div>
                        <div className="grid grid-cols-2 gap-2.5">
                          {[
                            ['medicament',  'Médicament *', 'Ex: Amoxicilline', true],
                            ['dosage',      'Dosage *',     'Ex: 500mg',         true],
                            ['frequence',   'Posologie *',  'Ex: 3x/jour',       true],
                            ['duree',       'Durée *',      'Ex: 7 jours',       true],
                          ].map(([field, label, placeholder, req]) => (
                            <div key={field}>
                              <label className="label-xs mb-1 block">{label}</label>
                              <input
                                type="text"
                                required={req}
                                placeholder={placeholder}
                                value={item[field]}
                                onChange={e => handleItemChange(i, field, e.target.value)}
                                className="input-base py-2"
                              />
                            </div>
                          ))}
                          <div className="col-span-2">
                            <label className="label-xs mb-1 block">Instructions spéciales</label>
                            <input
                              type="text"
                              placeholder="Ex: À prendre pendant les repas"
                              value={item.instructions}
                              onChange={e => handleItemChange(i, 'instructions', e.target.value)}
                              className="input-base py-2"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <label className={labelClass}>Instructions générales</label>
                  <textarea
                    rows={2}
                    value={form.notes_generales}
                    onChange={e => setField('notes_generales', e.target.value)}
                    placeholder="Repos, hydratation, éviter…"
                    className="input-base resize-none"
                  />
                </div>
              </form>

              {/* Live preview – always visible on xl, toggle on smaller screens */}
              <div className={`p-5 overflow-y-auto soft-scrollbar bg-slate-50/60 ${showPreview ? 'block' : 'hidden xl:block'}`}>
                <p className="label-xs mb-3 text-slate-400">Aperçu temps réel</p>
                <PrescriptionPreview form={form} consultations={consultations} />
              </div>
            </div>

            {/* ── Sticky footer – always visible ── */}
            <div className="px-6 py-4 border-t border-slate-100 bg-white flex gap-3 justify-end">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="btn-ghost px-5"
              >
                Annuler
              </button>
              <button
                type="submit"
                form="prescription-form"
                disabled={saving}
                className="btn-primary px-6 justify-center"
              >
                {saving
                  ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Enregistrement…</>
                  : <><FileText size={15} />Créer l&apos;ordonnance</>}
              </button>
            </div>
          </div>

          <style>{`@keyframes confirmIn { from{opacity:0;transform:scale(0.95) translateY(12px)} to{opacity:1;transform:scale(1) translateY(0)} }`}</style>
        </div>
      )}

      {confirmDelete && (
        <ConfirmModal
          title="Mettre à la corbeille ?"
          message={`L'ordonnance de ${confirmDelete.name} sera déplacée dans la corbeille.`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onClose={() => setConfirmDelete(null)}
        />
      )}

      {showTrash && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4" onClick={() => setShowTrash(false)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-rose-50 flex items-center justify-center text-rose-500"><Trash2 size={16} /></div>
                <div>
                  <div className="font-bold text-slate-800 text-sm">Corbeille — Ordonnances</div>
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
                  {trashItems.map(p => (
                    <div key={p.id} className="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-200 gap-4">
                      <div className="min-w-0">
                        <div className="font-semibold text-slate-800 text-sm truncate">{p.patient_nom}</div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          {p.cree_le && new Date(p.cree_le).toLocaleDateString('fr-FR')}
                          {p.medecin_nom && ` — ${p.medecin_nom}`}
                          {p.nb_medicaments > 0 && ` · ${p.nb_medicaments} médicament${p.nb_medicaments > 1 ? 's' : ''}`}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <button onClick={() => handleRestore(p.id)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-semibold transition-colors">
                          <RotateCcw size={13} /> Restaurer
                        </button>
                        <button onClick={() => handleDeleteForever(p.id)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-600 text-xs font-semibold transition-colors">
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