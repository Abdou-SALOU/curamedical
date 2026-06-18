import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, lazy, Suspense } from 'react'
import useAuthStore from './store/authStore'
import useThemeStore from './store/themeStore'
import PrivateRoute from './components/PrivateRoute'
import Layout from './components/Layout'
import ToastContainer from './components/ToastContainer'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'

// Pages chargées à la demande — allège le bundle initial
// (FullCalendar et Jitsi SDK ne sont téléchargés que si la page est visitée)
const PatientsPage = lazy(() => import('./pages/PatientsPage'))
const AppointmentsPage = lazy(() => import('./pages/AppointmentsPage'))
const ConsultationsPage = lazy(() => import('./pages/ConsultationsPage'))
const PrescriptionsPage = lazy(() => import('./pages/PrescriptionsPage'))
const AdminPage = lazy(() => import('./pages/AdminPage'))
const VideoPage = lazy(() => import('./pages/VideoPage'))
const TeleconsultationRoomPage = lazy(() => import('./pages/TeleconsultationRoomPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const PatientProfilePage = lazy(() => import('./pages/PatientProfilePage'))
const TrashPage = lazy(() => import('./pages/TrashPage'))
const UnauthorizedPage = lazy(() => import('./pages/UnauthorizedPage'))

function AppLoader() {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-surface z-50">
      <div className="flex flex-col items-center gap-5">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full border-4 border-emerald-500/20" />
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-emerald-500 animate-spin" />
          <div className="absolute inset-[6px] rounded-full bg-emerald-50 flex items-center justify-center">
            <span className="text-emerald-600 text-xl font-black" style={{ fontFamily: 'Manrope' }}>C</span>
          </div>
        </div>
        <p className="text-sm font-semibold text-slate-500 animate-pulse">Chargement de CuraMedical…</p>
      </div>
    </div>
  )
}

export default function App() {
  const { fetchMe, isAuthenticated, isLoading } = useAuthStore()
  const { init } = useThemeStore()

  useEffect(() => {
    init()
    if (isAuthenticated) fetchMe()
  }, [isAuthenticated, fetchMe, init])

  if (isLoading) return <AppLoader />

  return (
    <>
      <BrowserRouter>
        <Suspense fallback={<AppLoader />}>
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
          <Route path="/teleconsultation/:id" element={
            <PrivateRoute path="/teleconsultation/"><TeleconsultationRoomPage /></PrivateRoute>
          } />
          <Route path="/profile" element={
            <PrivateRoute path="/profile"><Layout><PatientProfilePage /></Layout></PrivateRoute>
          } />
          <Route path="/patients/trash" element={
            <PrivateRoute path="/patients"><Layout><TrashPage /></Layout></PrivateRoute>
          } />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </Suspense>
      </BrowserRouter>
      <ToastContainer />
    </>
  )
}
