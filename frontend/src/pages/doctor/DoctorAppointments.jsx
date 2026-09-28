import React, { useEffect, useState } from 'react';
import { Calendar, CheckCircle, X, Clock } from 'lucide-react';
import { appointmentsAPI, doctorsAPI } from '../../services/api';
import StatusBadge from '../../components/ui/StatusBadge';
import Modal from '../../components/ui/Modal';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

export default function DoctorAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading]           = useState(true);
  const [selected, setSelected]         = useState(null);
  const [form, setForm]                 = useState({ status: '', notes: '', follow_up_date: '' });
  const [saving, setSaving]             = useState(false);

  useEffect(() => {
    appointmentsAPI.list().then(r => setAppointments(r.data.appointments || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const openUpdate = (a) => {
    setSelected(a);
    setForm({ status: a.status, notes: a.notes || '', follow_up_date: a.follow_up_date ? new Date(a.follow_up_date).toISOString().slice(0, 16) : '' });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await appointmentsAPI.update(selected.id, { status: form.status, notes: form.notes, follow_up_date: form.follow_up_date ? new Date(form.follow_up_date).toISOString() : undefined });
      toast.success('Appointment updated');
      setSelected(null);
      appointmentsAPI.list().then(r => setAppointments(r.data.appointments || []));
    } catch { toast.error('Failed'); }
    finally { setSaving(false); }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-4xl space-y-5 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Appointments</h1>
      </div>
      <div className="space-y-3">
        {appointments.length === 0 ? (
          <div className="card text-center py-16 text-gray-400"><Calendar className="w-12 h-12 mx-auto mb-3 opacity-40" /><p>No appointments</p></div>
        ) : appointments.map(a => (
          <div key={a.id} className="card hover:shadow-md transition-shadow cursor-pointer" onClick={() => openUpdate(a)}>
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center"><Calendar className="w-5 h-5 text-primary-600" /></div>
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">Patient #{a.patient_id}</p>
                  <p className="text-sm text-gray-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {new Date(a.appointment_date).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status={a.status} />
                {a.follow_up_date && <span className="text-xs text-blue-600">Follow-up: {new Date(a.follow_up_date).toLocaleDateString()}</span>}
              </div>
            </div>
            {a.reason && <p className="text-sm text-gray-500 mt-2">Reason: {a.reason}</p>}
          </div>
        ))}
      </div>
      <Modal isOpen={!!selected} onClose={() => setSelected(null)} title="Update Appointment">
        <div className="space-y-4">
          <div>
            <label className="label">Status</label>
            <select className="input" value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
              <option value="requested">Requested</option><option value="confirmed">Confirmed</option>
              <option value="completed">Completed</option><option value="cancelled">Cancelled</option><option value="no_show">No Show</option>
            </select>
          </div>
          <div><label className="label">Doctor Notes</label><textarea rows={3} className="input resize-none" value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} /></div>
          <div><label className="label">Follow-up Date</label><input type="datetime-local" className="input" value={form.follow_up_date} onChange={e => setForm(f => ({ ...f, follow_up_date: e.target.value }))} /></div>
          <div className="flex gap-3">
            <button onClick={() => setSelected(null)} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button onClick={handleSave} disabled={saving} className="btn-primary flex-1 justify-center">
              {saving ? <span className="spinner" /> : <CheckCircle className="w-4 h-4" />} Save
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
