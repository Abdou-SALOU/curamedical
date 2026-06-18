import { Navigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

/**
 * Matrice d'accès par rôle
 *
 * Administrateur : système uniquement — PAS de données cliniques patients
 * Médecin        : accès clinique complet
 * Secrétaire     : patients + RDV + ordonnances (lecture) — PAS de consultations
 * Patient        : ses propres données uniquement
 */
const ROLE_ACCESS = {
  administrateur: ['/', '/admin'],
  medecin:        ['/', '/patients', '/appointments', '/consultations', '/prescriptions', '/video'],
  secretaire:     ['/', '/patients', '/appointments', '/prescriptions'],
  patient:        ['/', '/appointments', '/consultations', '/prescriptions', '/profile'],
}

const DYNAMIC_PREFIXES = {
  administrateur: [],
  medecin:        ['/teleconsultation/'],
  secretaire:     [],
  patient:        ['/teleconsultation/'],
}

export default function PrivateRoute({ children, path }) {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) return <Navigate to="/login" replace />

  if (user && path) {
    const role    = user.role
    const allowed = ROLE_ACCESS[role] || []
    const dynamic = DYNAMIC_PREFIXES[role] || []

    if (allowed.includes(path)) return children
    if (dynamic.some(prefix => path.startsWith(prefix))) return children

    return <Navigate to="/unauthorized" replace />
  }

  return children
}