import useToastStore from '../store/toastStore'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react'

const STYLES = {
  success: {
    bar: 'bg-emerald-500',
    icon: CheckCircle,
    iconClass: 'text-emerald-500',
    bg: 'bg-white border-emerald-200',
  },
  error: {
    bar: 'bg-rose-500',
    icon: XCircle,
    iconClass: 'text-rose-500',
    bg: 'bg-white border-rose-200',
  },
  warning: {
    bar: 'bg-amber-500',
    icon: AlertTriangle,
    iconClass: 'text-amber-500',
    bg: 'bg-white border-amber-200',
  },
  info: {
    bar: 'bg-sky-500',
    icon: Info,
    iconClass: 'text-sky-500',
    bg: 'bg-white border-sky-200',
  },
}

function Toast({ toast, onRemove }) {
  const style = STYLES[toast.type] || STYLES.info
  const Icon = style.icon

  return (
    <div
      className={`flex items-start gap-3 rounded-2xl border px-4 py-3.5 shadow-lg shadow-slate-900/10 min-w-[260px] max-w-[380px] ${style.bg}`}
      style={{ animation: 'toastIn 0.35s cubic-bezier(0.16,1,0.3,1) both' }}
    >
      <Icon size={18} className={`mt-0.5 shrink-0 ${style.iconClass}`} />
      <p className="flex-1 text-sm font-medium text-slate-800 leading-5">{toast.message}</p>
      <button
        onClick={() => onRemove(toast.id)}
        className="text-slate-400 hover:text-slate-600 transition-colors"
      >
        <X size={15} />
      </button>
      {/* Bottom progress bar */}
      <span
        className={`absolute bottom-0 left-0 h-0.5 ${style.bar} rounded-full`}
        style={{ animation: 'toastProgress 4s linear forwards', width: '100%' }}
      />
    </div>
  )
}

export default function ToastContainer() {
  const { toasts, removeToast } = useToastStore()

  return (
    <>
      <style>{`
        @keyframes toastIn {
          from { opacity: 0; transform: translateY(20px) scale(0.95); }
          to   { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes toastProgress {
          from { width: 100%; }
          to   { width: 0%; }
        }
      `}</style>
      <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-2.5 pointer-events-none">
        {toasts.map((t) => (
          <div key={t.id} className="relative pointer-events-auto overflow-hidden">
            <Toast toast={t} onRemove={removeToast} />
          </div>
        ))}
      </div>
    </>
  )
}
