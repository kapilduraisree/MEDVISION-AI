import React, { useEffect, useState } from 'react';
import { Users, FileText, Save, ChevronDown, ChevronUp } from 'lucide-react';
import { appointmentsAPI, doctorsAPI, reportsAPI } from '../../services/api';
import StatusBadge from '../../components/ui/StatusBadge';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';
import toast from 'react-hot-toast';

export default function DoctorPatients() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading]           = useState(true);
  const [expanded, setExpanded]         = useState(null);
  const [patientData, setPatientData]   = useState({});
  const [noteForm, setNoteForm]         = useState({ note_text: '', follow_up_date: '' });
  const [saving, setSaving]             = useState(false);

  useEffect(() => {
    appointmentsAPI.list().then(r => setAppointments(r.data.appointments || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const togglePatient = async (patientId) => {
    if (expanded === patientId) { setExpanded(null); return; }
    setExpanded(patientId);
    if (!patientData[patientId]) {
      try {
        const res = await doctorsAPI.viewPatient(patientId);
        setPatientData(prev => ({ ...prev, [patientId]: res.data }));
      } catch { toast.error('Could not load patient data'); }
    }
  };

  const addNote = async (patientId) => {
    if (!noteForm.note_text.trim()) return;
    setSaving(true);
    try {
      await doctorsAPI.addNote({ patient_id: patientId, note_text: noteForm.note_text, follow_up_date: noteForm.follow_up_date || undefined });
      toast.success('Note added');
      setNoteForm({ note_text: '', follow_up_date: '' });
    } catch { toast.error('Failed to add note'); }
    finally { setSaving(false); }
  };

  // Get unique patient IDs from appointments
  const patientIds = [...new Set(appointments.map(a => a.patient_id))];

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-4xl space-y-5 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Patients ({patientIds.length})</h1>
      </div>
      {patientIds.length === 0 ? (
        <div className="card text-center py-16 text-gray-400"><Users className="w-12 h-12 mx-auto mb-3 opacity-40" /><p>No patients yet</p></div>
      ) : (
        <div className="space-y-3">
          {patientIds.map(pid => {
            const pd = patientData[pid];
            const isOpen = expanded === pid;
            return (
              <div key={pid} className="card">
                <button onClick={() => togglePatient(pid)} className="w-full flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center font-bold text-primary-600">
                      {pd?.patient?.name?.[0] || 'P'}
                    </div>
                    <div className="text-left">
                      <p className="font-semibold text-gray-900 dark:text-white">{pd?.patient?.name || `Patient #${pid}`}</p>
                      {pd?.patient?.blood_group && <span className="text-xs bg-red-100 text-red-700 px-2 rounded">{pd.patient.blood_group}</span>}
                    </div>
                  </div>
                  {isOpen ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                </button>

                {isOpen && pd && (
                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      {pd.patient.known_allergies && <div className="p-2 bg-amber-50 dark:bg-amber-900/10 rounded"><p className="text-xs text-amber-700 font-medium">Known Allergies</p><p className="text-amber-800">{pd.patient.known_allergies}</p></div>}
                      {pd.patient.chronic_conditions && <div className="p-2 bg-blue-50 dark:bg-blue-900/10 rounded"><p className="text-xs text-blue-700 font-medium">Chronic Conditions</p><p className="text-blue-800">{pd.patient.chronic_conditions}</p></div>}
                    </div>

                    {/* Reports */}
                    {pd.recent_reports?.length > 0 && (
                      <div>
                        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Recent Reports</p>
                        <div className="space-y-2">
                          {pd.recent_reports.map(r => (
                            <div key={r.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                              <span className="flex items-center gap-2"><FileText className="w-4 h-4 text-primary-400" />{r.report_type?.replace(/_/g, ' ')}</span>
                              <div className="flex items-center gap-2">
                                {r.is_doctor_reviewed && <span className="text-xs text-green-600">✓ Reviewed</span>}
                                <span className="text-xs text-gray-400">{r.report_date ? new Date(r.report_date).toLocaleDateString() : ''}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Add Note */}
                    <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg space-y-3">
                      <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">Add Clinical Note</p>
                      <textarea rows={3} className="input resize-none" placeholder="Enter clinical notes..." value={noteForm.note_text} onChange={e => setNoteForm(f => ({ ...f, note_text: e.target.value }))} />
                      <input type="datetime-local" className="input" value={noteForm.follow_up_date} onChange={e => setNoteForm(f => ({ ...f, follow_up_date: e.target.value }))} placeholder="Follow-up date (optional)" />
                      <button onClick={() => addNote(pid)} disabled={saving} className="btn-primary">
                        {saving ? <span className="spinner" /> : <Save className="w-4 h-4" />} Save Note
                      </button>
                    </div>
                    <DisclaimerBox />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
