import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import AppLayout from './components/layout/AppLayout';
import { PageLoader } from './components/ui/LoadingSpinner';

// Auth pages
import LandingPage    from './pages/LandingPage';
import LoginPage      from './pages/auth/LoginPage';
import RegisterPage   from './pages/auth/RegisterPage';

// Patient pages
import PatientDashboard   from './pages/patient/PatientDashboard';
import PatientProfile     from './pages/patient/PatientProfile';
import SymptomsPage       from './pages/patient/SymptomsPage';
import VoiceInputPage     from './pages/patient/VoiceInputPage';
import UploadReportPage   from './pages/patient/UploadReportPage';
import ExplainReportPage  from './pages/patient/ExplainReportPage';
import PrescriptionPage   from './pages/patient/PrescriptionPage';
import MedicineScanPage   from './pages/patient/MedicineScanPage';
import MedicineInfoPage   from './pages/patient/MedicineInfoPage';
import DrugInteractionPage from './pages/patient/DrugInteractionPage';
import RemindersPage      from './pages/patient/RemindersPage';
import PharmacyBillPage   from './pages/patient/PharmacyBillPage';
import HealthTrendsPage   from './pages/patient/HealthTrendsPage';
import AISummaryPage      from './pages/patient/AISummaryPage';
import ChatbotPage        from './pages/patient/ChatbotPage';
import MedicalLockerPage  from './pages/patient/MedicalLockerPage';
import FamilyPage         from './pages/patient/FamilyPage';
import AppointmentsPage   from './pages/patient/AppointmentsPage';
import EmergencyPage      from './pages/patient/EmergencyPage';

// Doctor pages
import DoctorDashboard    from './pages/doctor/DoctorDashboard';
import DoctorPatients     from './pages/doctor/DoctorPatients';
import DoctorAppointments from './pages/doctor/DoctorAppointments';

// Admin pages
import AdminDashboard   from './pages/admin/AdminDashboard';
import AdminUsers       from './pages/admin/AdminUsers';
import AdminDoctors     from './pages/admin/AdminDoctors';
import AdminMedicines   from './pages/admin/AdminMedicines';
import AdminAuditLogs   from './pages/admin/AdminAuditLogs';

// Shared pages
import NotificationsPage from './pages/NotificationsPage';
import SettingsPage      from './pages/SettingsPage';

function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth();
  if (loading) return <PageLoader />;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />;
  return <AppLayout>{children}</AppLayout>;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <PageLoader />;
  if (user) {
    if (user.role === 'admin')  return <Navigate to="/admin/dashboard"  replace />;
    if (user.role === 'doctor') return <Navigate to="/doctor/dashboard" replace />;
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}

function AppRoutes() {
  const { user } = useAuth();

  // Apply dark mode on load
  useEffect(() => {
    if (user?.dark_mode) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  }, [user?.dark_mode]);

  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
      <Route path="/login"    element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />

      {/* Patient */}
      <Route path="/dashboard"        element={<ProtectedRoute roles={['patient']}><PatientDashboard /></ProtectedRoute>} />
      <Route path="/profile"          element={<ProtectedRoute roles={['patient']}><PatientProfile /></ProtectedRoute>} />
      <Route path="/symptoms"         element={<ProtectedRoute roles={['patient']}><SymptomsPage /></ProtectedRoute>} />
      <Route path="/voice-input"      element={<ProtectedRoute roles={['patient']}><VoiceInputPage /></ProtectedRoute>} />
      <Route path="/reports"          element={<ProtectedRoute roles={['patient']}><UploadReportPage /></ProtectedRoute>} />
      <Route path="/reports/:id"      element={<ProtectedRoute roles={['patient','doctor','admin']}><ExplainReportPage /></ProtectedRoute>} />
      <Route path="/prescriptions"    element={<ProtectedRoute roles={['patient']}><PrescriptionPage /></ProtectedRoute>} />
      <Route path="/medicines"        element={<ProtectedRoute roles={['patient','doctor','admin']}><MedicineInfoPage /></ProtectedRoute>} />
      <Route path="/medicine-scan"    element={<ProtectedRoute roles={['patient']}><MedicineScanPage /></ProtectedRoute>} />
      <Route path="/drug-interactions" element={<ProtectedRoute roles={['patient','doctor']}><DrugInteractionPage /></ProtectedRoute>} />
      <Route path="/reminders"        element={<ProtectedRoute roles={['patient']}><RemindersPage /></ProtectedRoute>} />
      <Route path="/pharmacy-bills"   element={<ProtectedRoute roles={['patient']}><PharmacyBillPage /></ProtectedRoute>} />
      <Route path="/health-trends"    element={<ProtectedRoute roles={['patient']}><HealthTrendsPage /></ProtectedRoute>} />
      <Route path="/ai-summary"       element={<ProtectedRoute roles={['patient']}><AISummaryPage /></ProtectedRoute>} />
      <Route path="/chatbot"          element={<ProtectedRoute><ChatbotPage /></ProtectedRoute>} />
      <Route path="/locker"           element={<ProtectedRoute roles={['patient']}><MedicalLockerPage /></ProtectedRoute>} />
      <Route path="/family"           element={<ProtectedRoute roles={['patient']}><FamilyPage /></ProtectedRoute>} />
      <Route path="/appointments"     element={<ProtectedRoute roles={['patient']}><AppointmentsPage /></ProtectedRoute>} />
      <Route path="/emergency"        element={<ProtectedRoute roles={['patient']}><EmergencyPage /></ProtectedRoute>} />

      {/* Doctor */}
      <Route path="/doctor/dashboard"    element={<ProtectedRoute roles={['doctor','admin']}><DoctorDashboard /></ProtectedRoute>} />
      <Route path="/doctor/patients"     element={<ProtectedRoute roles={['doctor','admin']}><DoctorPatients /></ProtectedRoute>} />
      <Route path="/doctor/appointments" element={<ProtectedRoute roles={['doctor','admin']}><DoctorAppointments /></ProtectedRoute>} />

      {/* Admin */}
      <Route path="/admin/dashboard"  element={<ProtectedRoute roles={['admin']}><AdminDashboard /></ProtectedRoute>} />
      <Route path="/admin/users"      element={<ProtectedRoute roles={['admin']}><AdminUsers /></ProtectedRoute>} />
      <Route path="/admin/doctors"    element={<ProtectedRoute roles={['admin']}><AdminDoctors /></ProtectedRoute>} />
      <Route path="/admin/medicines"  element={<ProtectedRoute roles={['admin']}><AdminMedicines /></ProtectedRoute>} />
      <Route path="/admin/audit-logs" element={<ProtectedRoute roles={['admin']}><AdminAuditLogs /></ProtectedRoute>} />

      {/* Shared */}
      <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
      <Route path="/settings"      element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster position="top-right" />
      </AuthProvider>
    </BrowserRouter>
  );
}
