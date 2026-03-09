import { Navigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const ROLE_ACCESS = {
  admin:     ['/', '/patients', '/appointments', '/consultations', '/prescriptions', '/admin'],
  doctor:    ['/', '/patients', '/appointments', '/consultations', '/prescriptions'],
  secretary: ['/', '/patients', '/appointments'],
}

export default function PrivateRoute({ children, path }) {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) return <Navigate to="/login" replace />

  if (user && path) {
    const allowed = ROLE_ACCESS[user.role] || []
    if (!allowed.includes(path)) {
      return <Navigate to="/unauthorized" replace />
    }
  }

  return children
}