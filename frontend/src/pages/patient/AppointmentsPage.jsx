import React, { useEffect, useState } from 'react';
import { Calendar, Plus, Search, Clock, CheckCircle } from 'lucide-react';
import { appointmentsAPI } from '../../services/api';
import Modal from '../../components/ui/Modal';
import StatusBadge from '../../components/ui/StatusBadge';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors]           = useState([]);
  const [loading, setLoading]           = useState(true);
  const [showBook, setShowBook]         = useState(false);
  const [specFilter, setSpecFilter]     = useState('');
  const [searching, setSearching]       = useState(false);
  const [booking, setBooking]           = useState(false);
  const [form, setForm] = useState({ doctor_id: '', appointment_date: '', reason: '' });

  const load = () => {
    appointmentsAPI.list().then(r => setAppointments(r.data.appointments || [])).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const searchDoctors = async () => {
    setSearching(true);
    try {
      const res = await appointmentsAPI.searchDoctors({ specialization: specFilter });
      setDoctors(res.data.doctors || []);
    } catch {} finally { setSearching(false); }
  };
  useEffect(() => { searchDoctors(); }, []);

  const handleBook = async (e) => {
    e.preventDefault();
    if (!form.doctor_id || !form.appointment_date) { toast.error('Select doctor and date'); return; }
    setBooking(true);
    try {
      await appointmentsAPI.create({ ...form, doctor_id: parseInt(form.doctor_id), appointment_date: new Date(form.appointment_date).toISOString() });
      toast.success('Appointment requested!');
      setShowBook(false); load();
    } catch { toast.error('Booking failed'); }
    finally { setBooking(false); }
  };

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  return (
    <div className="max-w-4xl space-y-5 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Appointments</h1>
          <p className="text-sm text-gray-500 mt-1">Manage your doctor appointments</p>
        </div>
        <button onClick={() => setShowBook(true)} className="btn-primary"><Plus className="w-4 h-4" />Book Appointment</button>
      </div>

      {loading ? <LoadingSpinner /> : appointments.length === 0 ? (
        <div className="card text-center py-16 text-gray-400">
          <Calendar className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="font-medium">No appointments yet</p>
          <button onClick={() => setShowBook(true)} className="btn-primary mt-4"><Plus className="w-4 h-4" />Book Your First Appointment</button>
        </div>
      ) : (
        <div className="space-y-3">
          {appointments.map(a => (
            <div key={a.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                    <Calendar className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {new Date(a.appointment_date).toLocaleDateString('en-IN', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })}
                    </p>
                    <p className="text-sm text-gray-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(a.appointment_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={a.status} />
                  {a.follow_up_date && (
                    <span className="text-xs text-blue-600 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />Follow-up: {new Date(a.follow_up_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
              {a.reason && <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">Reason: {a.reason}</p>}
              {a.notes && <p className="text-sm text-gray-500 mt-1 italic">Notes: {a.notes}</p>}
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showBook} onClose={() => setShowBook(false)} title="Book Appointment" size="lg">
        <div className="space-y-5">
          <div className="flex gap-2">
            <input className="input flex-1" placeholder="Search by specialization..." value={specFilter} onChange={e => setSpecFilter(e.target.value)} />
            <button onClick={searchDoctors} className="btn-secondary">{searching ? <span className="spinner" /> : <Search className="w-4 h-4" />}</button>
          </div>
          <div className="max-h-52 overflow-y-auto space-y-2 border border-gray-200 dark:border-gray-700 rounded-lg p-2">
            {doctors.length === 0 ? <p className="text-center text-sm text-gray-400 py-4">No doctors found</p> : doctors.map(d => (
              <button key={d.id} type="button" onClick={() => setForm(f => ({ ...f, doctor_id: d.id.toString() }))}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${form.doctor_id === d.id.toString() ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-transparent hover:bg-gray-50 dark:hover:bg-gray-700'}`}>
                <p className="font-medium text-sm text-gray-900 dark:text-white">{d.name}</p>
                <p className="text-xs text-gray-500">{d.specialization} · {d.hospital_name} · ₹{d.consultation_fee}</p>
              </button>
            ))}
          </div>
          <form onSubmit={handleBook} className="space-y-4">
            <div><label className="label">Date & Time *</label><input type="datetime-local" className="input" value={form.appointment_date} onChange={set('appointment_date')} required /></div>
            <div><label className="label">Reason for Visit</label><textarea rows={2} className="input resize-none" placeholder="Briefly describe reason..." value={form.reason} onChange={set('reason')} /></div>
            <div className="flex gap-3">
              <button type="button" onClick={() => setShowBook(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
              <button type="submit" disabled={booking} className="btn-primary flex-1 justify-center">
                {booking ? <span className="spinner" /> : <Calendar className="w-4 h-4" />}
                {booking ? 'Booking...' : 'Request Appointment'}
              </button>
            </div>
          </form>
        </div>
      </Modal>
    </div>
  );
}
