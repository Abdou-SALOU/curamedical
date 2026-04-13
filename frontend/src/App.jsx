import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import useAuthStore from './store/authStore'
import PrivateRoute from './components/PrivateRoute'
import Layout from './components/Layout'
import ToastContainer from './components/ToastContainer'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PatientsPage from './pages/PatientsPage'
import AppointmentsPage from './pages/AppointmentsPage'
import ConsultationsPage from './pages/ConsultationsPage'
import PrescriptionsPage from './pages/PrescriptionsPage'
import AdminPage from './pages/AdminPage'
import VideoPage from './pages/VideoPage'
import UnauthorizedPage from './pages/UnauthorizedPage'

function AppLoader() {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-surface z-50">
      <div className="flex flex-col items-center gap-5">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full border-4 border-emerald-500/20" />
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-emerald-500 animate-spin" />
          <div className="absolute inset-[6px] rounded-full bg-emerald-50 flex items-center justify-center">
            <span className="text-emerald-600 text-xl font-black" style={{ fontFamily: 'Manrope' }}>M</span>
          </div>
        </div>
        <p className="text-sm font-semibold text-slate-500 animate-pulse">Chargement de MedPredict…</p>
      </div>
    </div>
  )
}

export default function App() {
  const { fetchMe, isAuthenticated, isLoading } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) fetchMe()
  }, [isAuthenticated, fetchMe])

  // Block all routes until we know who the user is
  if (isLoading) return <AppLoader />

  return (
    <>
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
          <Route path="/admin" element={
            <PrivateRoute path="/admin"><Layout><AdminPage /></Layout></PrivateRoute>
          } />
          <Route path="/video" element={
            <PrivateRoute path="/video"><Layout><VideoPage /></Layout></PrivateRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      {/* Global toast layer – outside BrowserRouter so it always renders */}
      <ToastContainer />
    </>
  )
}