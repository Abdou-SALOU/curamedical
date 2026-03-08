import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'

export default function UnauthorizedPage() {
  const { user } = useAuthStore()

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-sm p-12 text-center max-w-md">
        <div className="text-6xl mb-4">🔒</div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Accès refusé</h1>
        <p className="text-gray-500 mb-2">
          Vous n'avez pas les droits nécessaires pour accéder à cette page.
        </p>
        {user && (
          <p className="text-sm text-gray-400 mb-6">
            Votre rôle : <span className="font-medium capitalize">{user.role}</span>
          </p>
        )}
        <Link
          to="/"
          className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium transition-all"
        >
          Retour au tableau de bord
        </Link>
      </div>
    </div>
  )
}