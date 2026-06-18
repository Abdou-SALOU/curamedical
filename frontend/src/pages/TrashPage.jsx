import { useEffect, useState, useCallback, useRef } from 'react'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import { SkeletonTable } from '../components/Skeleton'
import Pagination from '../components/Pagination'
import { Trash2, RotateCcw, ArrowLeft, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const PAGE_SIZE = 5

export default function TrashPage() {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const navigate = useNavigate()
  const debounceTimer = useRef(null)

  const fetchTrash = useCallback(async (query = '', pageNum = 1) => {
    try {
      const { data } = await api.get(
        `/api/patients/archives/?search=${encodeURIComponent(query)}&page=${pageNum}&page_size=${PAGE_SIZE}`
      )
      setPatients(data.results || data)
      setTotalCount(data.count !== undefined ? data.count : (data.results ? data.results.length : data.length))
    } catch {
      toast.error('Impossible de charger la corbeille.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    clearTimeout(debounceTimer.current)
    debounceTimer.current = setTimeout(() => fetchTrash(search, page), search ? 350 : 0)
    return () => clearTimeout(debounceTimer.current)
  }, [fetchTrash, search, page])

  const handleRestore = async (id) => {
    try {
      await api.post(`/api/patients/${id}/restaurer/`)
      toast.success('Patient restauré avec succès.')
      fetchTrash(search, page)
    } catch {
      toast.error('Erreur lors de la restauration.')
    }
  }

  return (
    <div className="p-5 md:p-6 space-y-5 min-h-screen">
      <section className="surface-panel rounded-3xl px-6 py-5">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/patients')}
            className="w-10 h-10 rounded-2xl bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-600 transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <p className="label-xs text-rose-600 font-bold">Corbeille</p>
            <h1 className="section-title mt-1 text-2xl font-black text-slate-900">Patients archives</h1>
          </div>
        </div>
      </section>

      <div className="surface-panel rounded-3xl overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100">
          <div className="relative">
            <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Rechercher dans la corbeille..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
                // Let the useEffect handle the fetch
              }}
              className="w-full rounded-2xl border border-slate-200 bg-white py-2.5 pl-11 pr-4 text-sm focus:border-rose-400 focus:outline-none focus:ring-3 focus:ring-rose-100 transition-all"
            />
          </div>
        </div>

        {loading ? (
          <SkeletonTable rows={5} cols={4} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  <th className="px-5 py-3.5 label-xs">Patient</th>
                  <th className="px-5 py-3.5 label-xs">CIN</th>
                  <th className="px-5 py-3.5 label-xs">Date d'archivage</th>
                  <th className="px-5 py-3.5 label-xs text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {patients.map(p => (
                  <tr key={p.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500 uppercase">
                          {p.prenom?.[0] || '?'}{p.nom?.[0] || ''}
                        </div>
                        <span className="text-sm font-medium text-slate-900">{p.nom_complet}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-600">{p.cin || '—'}</td>
                    <td className="px-5 py-3.5 text-sm text-slate-400 italic">
                      {p.modifie_le ? new Date(p.modifie_le).toLocaleDateString('fr-FR') : '—'}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={() => handleRestore(p.id)}
                        className="btn-ghost text-emerald-600 hover:bg-emerald-50 px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 ml-auto"
                      >
                        <RotateCcw size={14} /> Restaurer
                      </button>
                    </td>
                  </tr>
                ))}
                {patients.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-6 py-20 text-center">
                      <div className="flex flex-col items-center gap-3 text-slate-300">
                        <Trash2 size={40} strokeWidth={1.5} />
                        <p className="text-sm font-medium">La corbeille est vide</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
        {!loading && (
          <Pagination count={totalCount} currentPage={page} onPageChange={setPage} />
        )}
      </div>
    </div>
  )
}
