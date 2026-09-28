import axios from 'axios';

const BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 30000,
});

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle 401 – redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  register:  (data)  => api.post('/auth/register', data),
  login:     (email, password) => {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    return api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
  },
  logout:    ()      => api.post('/auth/logout'),
  getMe:     ()      => api.get('/auth/me'),
};

// ── Users ─────────────────────────────────────────────────────────────────────
export const usersAPI = {
  updateProfile:   (data) => api.put('/users/profile', data),
  uploadImage:     (form) => api.post('/users/profile-image', form),
  changePassword:  (data) => api.post('/users/change-password', data),
};

// ── Patients ──────────────────────────────────────────────────────────────────
export const patientsAPI = {
  getProfile:       ()     => api.get('/patients/profile'),
  updateProfile:    (data) => api.put('/patients/profile', data),
  getDashboard:     ()     => api.get('/patients/dashboard-summary'),
};

// ── Reports ───────────────────────────────────────────────────────────────────
export const reportsAPI = {
  upload:        (form)             => api.post('/reports/upload', form),
  list:          (params)           => api.get('/reports/', { params }),
  getDetail:     (id, lang)         => api.get(`/reports/${id}`, { params: { language: lang } }),
  correctValue:  (rid, vid, result) => api.put(`/reports/${rid}/values/${vid}`, null, { params: { result } }),
};

// ── Prescriptions ─────────────────────────────────────────────────────────────
export const prescriptionsAPI = {
  upload:   (form) => api.post('/prescriptions/upload', form),
  list:     ()     => api.get('/prescriptions/'),
  getOne:   (id)   => api.get(`/prescriptions/${id}`),
  verify:   (id)   => api.put(`/prescriptions/${id}/verify`),
};

// ── Medicines ─────────────────────────────────────────────────────────────────
export const medicinesAPI = {
  search:    (q)    => api.get('/medicines/search', { params: { q } }),
  getOne:    (id)   => api.get(`/medicines/${id}`),
  scanStrip: (form) => api.post('/medicines/scan-strip', form),
};

// ── Drug Interactions ─────────────────────────────────────────────────────────
export const drugInteractionsAPI = {
  check: (medicines) => api.post('/drug-interactions/check', { medicines }),
};

// ── Reminders ─────────────────────────────────────────────────────────────────
export const remindersAPI = {
  create:       (data)       => api.post('/reminders/', data),
  list:         ()           => api.get('/reminders/'),
  deactivate:   (id)         => api.delete(`/reminders/${id}`),
  log:          (id, data)   => api.post(`/reminders/${id}/log`, data),
  getAdherence: (id)         => api.get(`/reminders/${id}/adherence`),
};

// ── Pharmacy Bills ────────────────────────────────────────────────────────────
export const pharmacyBillsAPI = {
  upload:         (form)   => api.post('/pharmacy-bills/upload', form),
  list:           ()       => api.get('/pharmacy-bills/'),
  monthlyExpense: (year)   => api.get('/pharmacy-bills/monthly-expense', { params: { year } }),
};

// ── Appointments ──────────────────────────────────────────────────────────────
export const appointmentsAPI = {
  create:        (data)    => api.post('/appointments/', data),
  list:          ()        => api.get('/appointments/'),
  update:        (id, data)=> api.put(`/appointments/${id}`, data),
  searchDoctors: (params)  => api.get('/appointments/doctors/search', { params }),
};

// ── Chatbot ───────────────────────────────────────────────────────────────────
export const chatbotAPI = {
  sendMessage: (data)    => api.post('/chatbot/message', data),
  getHistory:  (session) => api.get('/chatbot/history', { params: { session_id: session } }),
  getSessions: ()        => api.get('/chatbot/sessions'),
};

// ── Health Metrics ────────────────────────────────────────────────────────────
export const healthMetricsAPI = {
  add:        (data)         => api.post('/health-metrics/', data),
  list:       (params)       => api.get('/health-metrics/', { params }),
  getTrends:  (params)       => api.get('/health-metrics/trends', { params }),
};

// ── Documents ─────────────────────────────────────────────────────────────────
export const documentsAPI = {
  upload: (form)           => api.post('/documents/upload', form),
  list:   (params)         => api.get('/documents/', { params }),
  delete: (id)             => api.delete(`/documents/${id}`),
};

// ── Family ────────────────────────────────────────────────────────────────────
export const familyAPI = {
  list:   ()       => api.get('/family/'),
  add:    (data)   => api.post('/family/', data),
  update: (id, d)  => api.put(`/family/${id}`, d),
  remove: (id)     => api.delete(`/family/${id}`),
};

// ── Emergency ─────────────────────────────────────────────────────────────────
export const emergencyAPI = {
  listContacts:  ()     => api.get('/emergency/contacts'),
  addContact:    (data) => api.post('/emergency/contacts', data),
  deleteContact: (id)   => api.delete(`/emergency/contacts/${id}`),
};

// ── Notifications ─────────────────────────────────────────────────────────────
export const notificationsAPI = {
  list:       (params)  => api.get('/notifications/', { params }),
  markRead:   (id)      => api.put(`/notifications/${id}/read`),
  markAllRead:()        => api.put('/notifications/mark-all-read'),
};

// ── Symptoms ──────────────────────────────────────────────────────────────────
export const symptomsAPI = {
  add:  (data) => api.post('/symptoms/', data),
  list: ()     => api.get('/symptoms/'),
};

// ── AI Summary ────────────────────────────────────────────────────────────────
export const aiSummaryAPI = {
  generate: (data) => api.post('/ai-summary/generate', data),
};

// ── Voice ─────────────────────────────────────────────────────────────────────
export const voiceAPI = {
  tts: (data) => api.post('/voice/tts', data, { responseType: 'blob' }),
  stt: (form) => api.post('/voice/stt', form),
};

// ── Doctors ───────────────────────────────────────────────────────────────────
export const doctorsAPI = {
  getProfile:    ()        => api.get('/doctors/profile'),
  updateProfile: (data)    => api.put('/doctors/profile', data),
  getDashboard:  ()        => api.get('/doctors/dashboard'),
  viewPatient:   (id)      => api.get(`/doctors/patients/${id}`),
  addNote:       (data)    => api.post('/doctors/notes', data),
};

// ── Admin ─────────────────────────────────────────────────────────────────────
export const adminAPI = {
  getAnalytics:        ()        => api.get('/admin/analytics'),
  listUsers:           (params)  => api.get('/admin/users', { params }),
  toggleUserActive:    (id)      => api.put(`/admin/users/${id}/toggle-active`),
  listDoctors:         (params)  => api.get('/admin/doctors', { params }),
  verifyDoctor:        (id)      => api.put(`/admin/doctors/${id}/verify`),
  addMedicine:         (data)    => api.post('/admin/medicines', data),
  addDrugInteraction:  (data)    => api.post('/admin/drug-interactions', data),
  getAuditLogs:        (params)  => api.get('/admin/audit-logs', { params }),
};
