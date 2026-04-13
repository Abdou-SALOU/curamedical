import { useEffect, useState, useCallback } from 'react'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import { SkeletonTable } from '../components/Skeleton'
import ConfirmModal from '../components/ConfirmModal'
import { FileText, Plus, Download, Trash2, Pill, X, Eye } from 'lucide-react'

const EMPTY_ITEM = { medication: '', dosage: '', frequency: '', duration: '', instructions: '' }
const EMPTY_FORM = { consultation: '', notes: '', items: [{ ...EMPTY_ITEM }] }

const inputClass = "input-base"
const labelClass = "label-xs mb-1.5 block"

/* ── Live prescription preview ──────────────────────────────── */
function PrescriptionPreview({ form, consultations }) {
  const consult = consultations.find(c => String(c.id) === String(form.consultation))
  const items = form.items.filter(i => i.medication.trim())

  return (
    <div className="rounded-2xl border-2 border-dashed border-slate-200 bg-white p-5 text-sm h-full min-h-[200px]">
      {/* Header mock */}
      <div className="flex items-start justify-between mb-5 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-5 h-5 rounded-md bg-emerald-500 flex items-center justify-center">
              <span className="text-white text-[9px] font-black">M</span>
            </div>
            <p className="font-black text-slate-900 text-base" style={{ fontFamily: 'Manrope' }}>MedPredict</p>
          </div>
          <p className="text-xs text-slate-400">Ordonnance médicale</p>
        </div>
        <p className="text-xs text-slate-400">{new Date().toLocaleDateString('fr-FR')}</p>
      </div>

      {/* Patient / Diagnosis */}
      {consult ? (
        <div className="mb-4">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Patient</p>
          <p className="font-semibold text-slate-800">{consult.patient_name || '—'}</p>
          <p className="text-xs text-slate-400 mt-0.5">Diagnostic : {consult.diagnosis || '—'}</p>
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
                <p className="font-bold text-slate-900">{item.medication} {item.dosage && `· ${item.dosage}`}</p>
                {item.frequency && <p className="text-slate-500">{item.frequency}{item.duration && ` — ${item.duration}`}</p>}
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

      {form.notes && (
        <div className="mt-3 p-2.5 rounded-xl bg-amber-50 border border-amber-100 text-xs text-amber-800">
          <span className="font-semibold">Instructions : </span>{form.notes}
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
  const [consultations, setConsultations] = useState([])
  const [showForm, setShowForm]     = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [form, setForm]             = useState(EMPTY_FORM)
  const [listLoading, setListLoading] = useState(true)
  const [saving, setSaving]         = useState(false)
  const [downloading, setDownloading] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const fetchAll = useCallback(async () => {
    try {
      const [prescs, consults] = await Promise.all([
        api.get('/api/prescriptions/'),
        api.get('/api/consultations/'),
      ])
      setPrescriptions(prescs.data.results || prescs.data)
      setConsultations(consults.data.results || consults.data)
    } catch {
      toast.error('Impossible de charger les ordonnances.')
    }
  }, [])

  useEffect(() => { fetchAll().finally(() => setListLoading(false)) }, [fetchAll])

  const handleItemChange = (index, field, value) => {
    setForm(prev => {
      const items = [...prev.items]
      items[index] = { ...items[index], [field]: value }
      return { ...prev, items }
    })
  }
  const addItem = () => setForm(prev => ({ ...prev, items: [...prev.items, { ...EMPTY_ITEM }] }))
  const removeItem = (i) => setForm(prev => ({ ...prev, items: prev.items.filter((_, idx) => idx !== i) }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/api/prescriptions/', form)
      setShowForm(false)
      setForm(EMPTY_FORM)
      await fetchAll()
      toast.success("Ordonnance créée avec succès !")
    } catch {
      toast.error("Erreur lors de la création de l'ordonnance.")
    } finally {
      setSaving(false)
    }
  }

  const handleDownload = async (id) => {
    setDownloading(id)
    try {
      const response = await api.get(`/api/prescriptions/${id}/pdf/`, { responseType: 'blob' })
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
    await api.delete(`/api/prescriptions/${id}/`)
    setPrescriptions(prev => prev.filter(p => p.id !== id))
    toast.success('Ordonnance supprimée.')
  }

  const setField = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  return (
    <div className="p-5 md:p-6 space-y-5 max-w-[1400px]">

      {/* Header */}
      <section className="surface-panel rounded-3xl px-6 py-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="label-xs text-emerald-700">Documents médicaux</p>
            <h1 className="section-title mt-1.5 text-3xl font-black text-slate-900">Ordonnances</h1>
            <p className="mt-1 text-sm text-slate-500">{prescriptions.length} ordonnance{prescriptions.length > 1 ? 's' : ''}</p>
          </div>
          <button onClick={() => setShowForm(true)} className="btn-primary self-start sm:self-auto">
            <Plus size={16} />
            Nouvelle ordonnance
          </button>
        </div>
      </section>

      {/* Table */}
      <div className="surface-panel rounded-3xl overflow-hidden">
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
                      <p className="text-sm font-semibold text-slate-900">{p.patient_name || '—'}</p>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">{p.doctor_name || '—'}</td>
                    <td className="px-5 py-3.5">
                      <div className="flex flex-wrap gap-1">
                        {(p.items || []).slice(0, 3).map((item, i) => (
                          <span key={i} className="badge badge-emerald">{item.medication}</span>
                        ))}
                        {(p.items || []).length > 3 && (
                          <span className="badge badge-slate">+{p.items.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">
                      {new Date(p.created_at).toLocaleDateString('fr-FR')}
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
                          onClick={() => setConfirmDelete({ id: p.id, name: p.patient_name })}
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
      </div>

      {/* ── Create form modal ── */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-sm overflow-y-auto">
          <div
            className="surface-panel-strong w-full max-w-4xl rounded-3xl overflow-hidden my-4"
            style={{ animation: 'confirmIn 0.3s cubic-bezier(0.16,1,0.3,1) both' }}
          >
            {/* Modal header */}
            <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
              <div>
                <p className="label-xs text-emerald-700">Documents médicaux</p>
                <h2 className="section-title text-xl font-black text-slate-900 mt-1">Nouvelle ordonnance</h2>
              </div>
              <div className="flex items-center gap-2">
                {/* Preview toggle on mobile */}
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

            <div className="grid xl:grid-cols-[1fr_340px] divide-x divide-slate-100 max-h-[80vh] overflow-hidden">
              {/* Form */}
              <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto soft-scrollbar">
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
                        {c.patient_name} — {c.diagnosis} ({new Date(c.created_at).toLocaleDateString('fr-FR')})
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
                    {form.items.map((item, i) => (
                      <div key={i} className="rounded-2xl bg-slate-50 border border-slate-100 p-4">
                        <div className="flex justify-between items-center mb-3">
                          <div className="flex items-center gap-2">
                            <Pill size={14} className="text-emerald-600" />
                            <span className="text-sm font-semibold text-slate-700">Médicament {i + 1}</span>
                          </div>
                          {form.items.length > 1 && (
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
                            ['medication',    'Médicament *', 'Ex: Amoxicilline', true],
                            ['dosage',        'Dosage *',     'Ex: 500mg',         true],
                            ['frequency',     'Posologie *',  'Ex: 3x/jour',       true],
                            ['duration',      'Durée *',      'Ex: 7 jours',       true],
                          ].map(([field, label, placeholder, required]) => (
                            <div key={field}>
                              <label className="label-xs mb-1 block">{label}</label>
                              <input
                                type="text"
                                required={required}
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
                    value={form.notes}
                    onChange={e => setField('notes', e.target.value)}
                    placeholder="Repos, hydratation, éviter…"
                    className="input-base resize-none"
                  />
                </div>

                <div className="flex gap-3 pt-1">
                  <button type="button" onClick={() => setShowForm(false)} className="btn-ghost flex-1">Annuler</button>
                  <button type="submit" disabled={saving} className="btn-primary flex-1 justify-center">
                    {saving ? 'Enregistrement…' : "Créer l'ordonnance"}
                  </button>
                </div>
              </form>

              {/* Live preview – always visible on xl, toggle on smaller screens */}
              <div className={`p-5 overflow-y-auto soft-scrollbar bg-slate-50/60 ${showPreview ? 'block' : 'hidden xl:block'}`}>
                <p className="label-xs mb-3 text-slate-400">Aperçu temps réel</p>
                <PrescriptionPreview form={form} consultations={consultations} />
              </div>
            </div>
          </div>

          <style>{`@keyframes confirmIn { from{opacity:0;transform:scale(0.95) translateY(12px)} to{opacity:1;transform:scale(1) translateY(0)} }`}</style>
        </div>
      )}

      {/* Confirm delete */}
      {confirmDelete && (
        <ConfirmModal
          title="Supprimer l'ordonnance ?"
          message={`L'ordonnance de ${confirmDelete.name} sera définitivement supprimée.`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onClose={() => setConfirmDelete(null)}
        />
      )}
    </div>
  )
}