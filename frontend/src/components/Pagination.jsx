import { ChevronLeft, ChevronRight } from 'lucide-react'

/**
 * Pagination améliorée avec numéros de page cliquables et ellipsis.
 * Remonte automatiquement en haut de liste au changement de page.
 */
export default function Pagination({ count, pageSize = 5, currentPage, onPageChange }) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize))

  const handleChange = (page) => {
    if (page < 1 || page > totalPages || page === currentPage) return
    onPageChange(page)
    // Remonter en haut de la liste après changement de page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Génère la liste des numéros à afficher (avec ellipsis)
  const getPages = () => {
    if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)
    const pages = []
    // Toujours afficher la 1ère page
    pages.push(1)
    if (currentPage > 3) pages.push('...')
    // Pages autour de la page courante
    const start = Math.max(2, currentPage - 1)
    const end = Math.min(totalPages - 1, currentPage + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (currentPage < totalPages - 2) pages.push('...')
    // Toujours afficher la dernière page
    pages.push(totalPages)
    return pages
  }

  if (totalPages <= 1 && count <= pageSize) return null

  return (
    <div className="flex items-center justify-between px-5 py-3 border-t border-slate-100 bg-slate-50/50">
      {/* Infos */}
      <span className="text-xs text-slate-500 font-medium hidden sm:block">
        Page <span className="font-bold text-slate-700">{currentPage}</span> sur {totalPages}
        <span className="mx-2 text-slate-300">|</span>
        <span className="font-bold text-slate-700">{count}</span> résultat{count > 1 ? 's' : ''}
      </span>
      <span className="text-xs text-slate-500 font-medium sm:hidden">
        {currentPage}/{totalPages}
      </span>

      {/* Contrôles */}
      <div className="flex items-center gap-1">
        {/* Précédent */}
        <button
          onClick={() => handleChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-bold text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:pointer-events-none transition-all shadow-sm"
          title="Page précédente"
        >
          <ChevronLeft size={14} />
          <span className="hidden sm:inline">Préc.</span>
        </button>

        {/* Numéros de page */}
        <div className="flex items-center gap-1">
          {getPages().map((page, i) =>
            page === '...' ? (
              <span key={`ellipsis-${i}`} className="w-8 text-center text-xs text-slate-400 font-bold select-none">
                …
              </span>
            ) : (
              <button
                key={page}
                onClick={() => handleChange(page)}
                className={`min-w-[32px] h-8 rounded-xl text-xs font-bold transition-all ${
                  page === currentPage
                    ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/25 scale-105'
                    : 'bg-white text-slate-600 border border-slate-200 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200'
                }`}
              >
                {page}
              </button>
            )
          )}
        </div>

        {/* Suivant */}
        <button
          onClick={() => handleChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-bold text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 hover:border-slate-300 disabled:opacity-40 disabled:pointer-events-none transition-all shadow-sm"
          title="Page suivante"
        >
          <span className="hidden sm:inline">Suiv.</span>
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}
