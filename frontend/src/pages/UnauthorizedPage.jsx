import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'

export default function UnauthorizedPage() {
  const { user } = useAuthStore()

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center p-6">
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-error/5 blur-[120px]" />
      </div>

      <div className="bg-surface-container-lowest rounded-3xl ghost-border p-12 text-center max-w-md w-full"
        style={{ boxShadow: '0 20px 40px rgba(25,28,30,0.06)' }}>
        <div className="w-16 h-16 bg-error-container rounded-2xl flex items-center justify-center mx-auto mb-6">
          <span className="material-symbols-outlined text-error text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>
            lock
          </span>
        </div>
        <h1 className="text-2xl font-bold text-on-surface mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Accès refusé
        </h1>
        <p className="text-on-surface-variant mb-3 text-sm">
          Vous n'avez pas les droits nécessaires pour accéder à cette page.
        </p>
        {user && (
          <p className="text-xs text-on-surface-variant/60 mb-8">
            Votre rôle : <span className="font-semibold capitalize text-on-surface-variant">{user.role}</span>
          </p>
        )}
        <Link
          to="/"
          className="inline-flex items-center gap-2 primary-gradient text-white px-6 py-3 rounded-xl font-semibold text-sm transition-all hover:-translate-y-0.5"
          style={{ boxShadow: '0 4px 12px rgba(0,104,95,0.2)' }}
        >
          <span className="material-symbols-outlined text-lg">arrow_back</span>
          Retour au tableau de bord
        </Link>
      </div>
    </div>
  )
}