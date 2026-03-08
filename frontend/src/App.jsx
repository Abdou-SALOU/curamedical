import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import useAuthStore from './store/authStore'
import PrivateRoute from './components/PrivateRoute'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PatientsPage from './pages/PatientsPage'
import AppointmentsPage from './pages/AppointmentsPage'
import ConsultationsPage from './pages/ConsultationsPage'
import PrescriptionsPage from './pages/PrescriptionsPage'
import UnauthorizedPage from './pages/UnauthorizedPage'

export default function App() {
  const { fetchMe, isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) fetchMe()
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        <Route path="/" element={
          <PrivateRoute path="/"><Layout><DashboardPage /></Layout></PrivateRoute>
        } />
        <Route path="/patients" element={
          <PrivateRoute path="/patients"><Layout><PatientsPage /></Layout></PrivateRoute>
        } />
        <Route path="/appointments" element={
          <PrivateRoute path="/appointments"><Layout><AppointmentsPage /></Layout></PrivateRoute>
        } />
        <Route path="/consultations" element={
          <PrivateRoute path="/consultations"><Layout><ConsultationsPage /></Layout></PrivateRoute>
        } />
        <Route path="/prescriptions" element={
          <PrivateRoute path="/prescriptions"><Layout><PrescriptionsPage /></Layout></PrivateRoute>
        } />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}