import { Navigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const ROLE_ACCESS = {
  admin:     ['/', '/patients', '/appointments', '/consultations', '/prescriptions', '/admin', '/video'],
  doctor:    ['/', '/patients', '/appointments', '/consultations', '/prescriptions', '/video'],
  secretary: ['/', '/patients', '/appointments'],
  patient:   ['/', '/appointments', '/consultations', '/prescriptions', '/video'],
}

export default function PrivateRoute({ children, path }) {
  const { isAuthenticated, user } = useAuthStore()

  // App.jsx already waits for isLoading=false before rendering routes,
  // so here we just guard against unauthenticated access
  if (!isAuthenticated) return <Navigate to="/login" replace />

  if (user && path) {
    const allowed = ROLE_ACCESS[user.role] || []
    if (!allowed.includes(path)) return <Navigate to="/unauthorized" replace />
  }

  return children
}