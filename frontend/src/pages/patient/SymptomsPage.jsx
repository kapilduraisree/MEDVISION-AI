import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Plus, Mic, AlertTriangle, Clock } from 'lucide-react';
import { symptomsAPI } from '../../services/api';
import { EmergencyBox, DisclaimerBox } from '../../components/ui/DisclaimerBox';
import toast from 'react-hot-toast';

const SEVERITIES = ['mild', 'moderate', 'severe'];

export default function SymptomsPage() {
  const [symptoms, setSymptoms]     = useState([]);
  const [form, setForm]             = useState({ description: '', severity: 'mild', duration: '', location_on_body: '', language: 'en' });
  const [submitting, setSubmitting] = useState(false);
  const [emergency, setEmergency]   = useState(null);

  const loadSymptoms = () => {
    symptomsAPI.list().then(r => setSymptoms(r.data.symptoms || [])).catch(() => {});
  };
  useEffect(() => { loadSymptoms(); }, []);

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.description.trim()) return;
    setSubmitting(true);
    try {
      const res = await symptomsAPI.add(form);
      if (res.data.is_emergency_flagged) {
        setEmergency(res.data.emergency_message);
      } else {
        toast.success('Symptoms recorded');
      }
      setForm({ description: '', severity: 'mild', duration: '', location_on_body: '', language: 'en' });
      loadSymptoms();
    } catch {
      toast.error('Failed to save symptoms');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Symptom Tracker</h1>
          <p className="text-sm text-gray-500 mt-1">Record your symptoms for your health history</p>
        </div>
        <Link to="/voice-input" className="btn-secondary">
          <Mic className="w-4 h-4" /> Voice Input
        </Link>
      </div>

      {emergency && <EmergencyBox text={emergency} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="card">
          <h2 className="section-title flex items-center gap-2"><Plus className="w-4 h-4" /> Add Symptoms</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Describe your symptoms *</label>
              <textarea
                rows={4} className="input resize-none"
                placeholder="e.g. Headache and mild fever for past 2 days..."
                value={form.description} onChange={set('description')} required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Severity</label>
                <select className="input" value={form.severity} onChange={set('severity')}>
                  {SEVERITIES.map(s => <option key={s} value={s} className="capitalize">{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Duration</label>
                <input className="input" placeholder="e.g. 2 days" value={form.duration} onChange={set('duration')} />
              </div>
            </div>
            <div>
              <label className="label">Body Location (optional)</label>
              <input className="input" placeholder="e.g. Head, chest, stomach" value={form.location_on_body} onChange={set('location_on_body')} />
            </div>
            <div>
              <label className="label">Language</label>
              <select className="input" value={form.language} onChange={set('language')}>
                <option value="en">English</option>
                <option value="ta">தமிழ் (Tamil)</option>
              </select>
            </div>
            <button type="submit" className="btn-primary w-full justify-center" disabled={submitting}>
              {submitting ? <span className="spinner" /> : <Activity className="w-4 h-4" />}
              {submitting ? 'Saving...' : 'Record Symptoms'}
            </button>
          </form>
          <DisclaimerBox text="This system does not diagnose medical conditions. If you have severe symptoms, seek immediate medical attention." />
        </div>

        {/* History */}
        <div className="card">
          <h2 className="section-title flex items-center gap-2"><Clock className="w-4 h-4" /> Symptom History</h2>
          {symptoms.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Activity className="w-10 h-10 mx-auto mb-2 opacity-40" />
              <p className="text-sm">No symptoms recorded yet</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {symptoms.map(s => (
                <div key={s.id} className={`p-3 rounded-lg border ${s.is_emergency_flagged ? 'border-red-300 bg-red-50 dark:bg-red-900/10' : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700'}`}>
                  {s.is_emergency_flagged && (
                    <div className="flex items-center gap-1 text-red-600 text-xs font-medium mb-1">
                      <AlertTriangle className="w-3 h-3" /> Emergency Flagged
                    </div>
                  )}
                  <p className="text-sm text-gray-800 dark:text-gray-200">{s.description}</p>
                  <div className="flex items-center gap-3 mt-1">
                    {s.severity && (
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        s.severity === 'severe' ? 'bg-red-100 text-red-700' :
                        s.severity === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>{s.severity}</span>
                    )}
                    <span className="text-xs text-gray-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(s.created_at).toLocaleDateString()}
                    </span>
                    {s.input_method === 'voice' && <span className="text-xs text-blue-500 flex items-center gap-1"><Mic className="w-3 h-3" />Voice</span>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
