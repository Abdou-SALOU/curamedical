import { useState } from 'react'
import { AlertTriangle, X } from 'lucide-react'

/**
 * Reusable confirmation modal – replaces window.confirm()
 * 
 * Usage:
 *   const [confirmState, setConfirmState] = useState(null)
 *   <ConfirmModal {...confirmState} onClose={() => setConfirmState(null)} />
 *   
 *   setConfirmState({
 *     title: 'Supprimer?',
 *     message: 'Cette action est irréversible.',
 *     onConfirm: () => doDelete(),
 *     variant: 'danger' // or 'warning'
 *   })
 */
export default function ConfirmModal({ title, message, onConfirm, onClose, variant = 'danger' }) {
  const [busy, setBusy] = useState(false)

  if (!onClose) return null

  const handleConfirm = async () => {
    setBusy(true)
    try { await onConfirm?.() }
    finally { setBusy(false); onClose() }
  }

  const isDanger = variant === 'danger'

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-3xl border border-slate-200 shadow-2xl shadow-slate-900/20 p-7 w-full max-w-sm"
        style={{ animation: 'confirmIn 0.3s cubic-bezier(0.16,1,0.3,1) both' }}
      >
        {/* Icon */}
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-5 ${isDanger ? 'bg-rose-50' : 'bg-amber-50'}`}>
          <AlertTriangle size={22} className={isDanger ? 'text-rose-500' : 'text-amber-500'} />
        </div>

        <h3 className="text-lg font-black text-slate-900 mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
          {title || 'Confirmer'}
        </h3>
        <p className="text-sm text-slate-500 leading-6 mb-7">{message}</p>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-xl bg-slate-100 text-slate-700 text-sm font-semibold hover:bg-slate-200 transition-colors"
          >
            Annuler
          </button>
          <button
            onClick={handleConfirm}
            disabled={busy}
            className={`flex-1 py-2.5 rounded-xl text-white text-sm font-semibold transition-all disabled:opacity-60 ${
              isDanger
                ? 'bg-rose-500 hover:bg-rose-600'
                : 'bg-amber-500 hover:bg-amber-600'
            }`}
          >
            {busy ? 'En cours...' : 'Confirmer'}
          </button>
        </div>
      </div>

      <style>{`
        @keyframes confirmIn {
          from { opacity: 0; transform: scale(0.94) translateY(10px); }
          to   { opacity: 1; transform: scale(1) translateY(0); }
        }
      `}</style>
    </div>
  )
}
